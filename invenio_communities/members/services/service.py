# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Service."""

from elasticsearch_dsl.query import Q
from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.records import RecordService
from invenio_records_resources.services.uow import RecordCommitOp, \
    RecordDeleteOp, unit_of_work
from sqlalchemy.orm.exc import NoResultFound

from ...permissions import create_community_role_need
from ..errors import LastOwnerError, OwnerSelfRoleChangeError, \
    ManagerSelfRoleChangeError


class MemberService(RecordService):
    """Member Service."""

    @property
    def community_cls(self):
        """Return community class."""
        return self.config.community_cls

    @unit_of_work()
    def create(self, identity, data, uow=None):
        """Create member."""
        community_id = data.get("community")
        community_record = self.community_cls.get_record(community_id)

        self.require_permission(
            identity, "create_member", record=community_record
        )

        # Validate data (if there are errors, .load() raises)
        data, errors = self.schema.load(
            data,
            context={"identity": identity},
        )

        member_record = self.record_cls.create(
            {},
            community_id=data.get("community"),
            user_id=data.get("user"),
            role=data.get("role")
        )

        # Persist record (DB and index)
        uow.register(RecordCommitOp(member_record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            member_record,
            links_tpl=self.links_item_tpl,
        )

    def read(self, identity, id_):
        """Read member record.

        :param id_: a dict of the primary keys
        """
        member_record = self.record_cls.get_record(id_)

        self.require_permission(identity, "read_member", record=member_record)

        return self.result_item(
            self,
            identity,
            member_record,
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None):
        """Replace a record."""
        member_record = self.record_cls.get_record(id_)

        self.check_revision_id(member_record, revision_id)

        # Permissions
        self.require_permission(
            identity, "update_member", record=member_record
        )

        data, _ = self.schema.load(
            data,
            context=dict(
                identity=identity,
                record=member_record
            )
        )

        self._assert_can_change_role(identity, member_record)

        member_record.update(
            dict(
                community_id=data.get("community"),
                user_id=data.get("user"),
                role=data.get("role")
            )
        )

        uow.register(RecordCommitOp(member_record, self.indexer))

        return self.result_item(
            self,
            identity,
            member_record,
            links_tpl=self.links_item_tpl,
        )

    def _assert_can_change_role(self, identity, member_record):
        """Raises if identity can't change role."""
        # Owner/Manager trying to change their role
        # TODO? account for group maybe (we do want person owner though...)
        if identity.id == member_record.user_id:
            if member_record.role == "owner":
                raise OwnerSelfRoleChangeError()
            if member_record.role == "manager":
                raise ManagerSelfRoleChangeError()

        # Manager trying to change owner
        manager_need = create_community_role_need(
            member_record.community_id, "manager"
        )
        if manager_need in identity.provides and member_record.role == "owner":
            raise PermissionDeniedError()

    @unit_of_work()
    def delete(self, identity, id_, revision_id=None, uow=None):
        """Delete member."""
        member_record = self.record_cls.get_record(id_)

        self.check_revision_id(member_record, revision_id)

        # Permissions
        self.require_permission(
            identity, "delete_member", record=member_record
        )

        # Check if last owner
        if self._deleting_last_owner(identity, member_record):
            raise LastOwnerError()

        # Run components
        self.run_components(
            'delete_member', identity, record=member_record, uow=uow
        )

        uow.register(
            RecordDeleteOp(member_record, self.indexer, index_refresh=True)
        )

        return True

    def _deleting_last_owner(self, identity, member_record):
        """Check if member_record is last owner of its community."""
        if member_record.role != "owner":
            return False

        search = self._search(
            'search_members',
            identity,
            params={},
            es_preference=None,
            permission_action='read_search_members',
            extra_filter=(
                Q('term', community_id=str(member_record.community_id)) &
                Q('term', role="owner")
            )
        )

        owners = [h for h in search.execute()]

        return len(owners) == 1

    def search(
            self, identity, community_id, params=None, es_preference=None,
            **kwargs):
        """Search for records matching the querystring."""
        # community id is the uuid for now
        community_record = self.community_cls.get_record(community_id)

        self.require_permission(
            identity, 'search_members', record=community_record
        )

        # Prepare and execute the search
        params = params or {}
        # Using permission_action='read_search_members' leverages the already
        # done search_members check.
        search = self._search(
            'search_members', identity, params, es_preference,
            permission_action='read_search_members', **kwargs)
        search_result = search.execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(self.config.links_search, context={
                "args": params
            }),
            links_item_tpl=self.links_item_tpl,
        )

    def get_member(self, community_uuid, user_id):
        """Get member associated with community and user ids."""
        return self.record_cls.model_cls.query.filter_by(
            community_id=community_uuid,
            user_id=user_id,
        ).one()

    def is_member(self, community_uuid, user_id):
        """Check if member exists based on community and user ids."""
        try:
            self.get_member(community_uuid, user_id)
        except NoResultFound:
            return False

        return True
