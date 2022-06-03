# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
# Copyright (C) 2021-2022 Northwestern University.
# Copyright (C)      2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Service API."""

from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from flask import current_app
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.records import (
    RecordService,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordIndexOp,
    unit_of_work,
)
from invenio_requests import current_requests_service
from invenio_requests.services.results import EntityResolverExpandableField
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from invenio_communities.communities.records.models import CommunityFeatured
from invenio_communities.communities.services.uow import (
    CommunityFeaturedCommitOp,
    CommunityFeaturedDeleteOp,
)
from invenio_communities.errors import (
    CommunityFeaturedEntryDoesNotExistError,
    LogoSizeLimitError,
)
from invenio_communities.generators import CommunityMembers


class CommunityService(RecordService):
    """community Service."""

    def __init__(
        self, config, files_service=None, invitations_service=None, members_service=None
    ):
        """Constructor for CommunityService."""
        super().__init__(config)
        self._files = files_service
        self._invitations = invitations_service
        self._members = members_service

    @property
    def files(self):
        """Community files service."""
        return self._files

    @property
    def invitations(self):
        """Community invitations service."""
        return self._invitations

    @property
    def members(self):
        """Community members service."""
        return self._members

    @property
    def schema_featured(self):
        """Returns the featured data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_featured)

    @property
    def expandable_fields(self):
        """Get expandable fields."""
        return [
            EntityResolverExpandableField("created_by"),
            EntityResolverExpandableField("receiver"),
        ]

    def search_user_communities(
        self, identity, params=None, es_preference=None, **kwargs
    ):
        """Search for records matching the querystring."""
        self.require_permission(identity, "search_user_communities")

        # Prepare and execute the search
        params = params or {}
        search_result = self._search(
            "search",
            identity,
            params,
            es_preference,
            permission_action=None,
            extra_filter=CommunityMembers().query_filter(identity),
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_user_search, context={"args": params}
            ),
            links_item_tpl=self.links_item_tpl,
        )

    def search_community_requests(
        self,
        identity,
        community_id,
        params=None,
        es_preference=None,
        expand=False,
        **kwargs
    ):
        """Search for requests of a specific community."""
        self.require_permission(identity, "search_requests", community_id=community_id)

        # Prepare and execute the search
        params = params or {}
        search_result = current_requests_service._search(
            "search",
            identity,
            params,
            es_preference,
            permission_action=None,
            extra_filter=Q("term", **{"receiver.community": community_id}),
            **kwargs
        ).execute()

        return current_requests_service.result_list(
            current_requests_service,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_community_requests_search,
                context={"args": params, "community_id": community_id},
            ),
            links_item_tpl=current_requests_service.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def rename(
        self, identity, id_, data, revision_id=None, raise_errors=True, uow=None
    ):
        """Rename a community."""
        record = self.record_cls.pid.resolve(id_)
        old_slug = record.slug

        self.check_revision_id(record, revision_id)

        # Permissions
        self.require_permission(identity, "rename", record=record)

        if "slug" not in data:
            raise ValidationError(
                "Missing data for required field.",
                field_name="slug",
            )

        data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,  # if False, flow is continued with
            schema_args={"partial": True}  # data only containing valid data,
            # but errors are reported
        )  # (as warnings)

        # Run components
        self.run_components(
            "rename", identity, data=data, record=record, old_slug=old_slug, uow=uow
        )

        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def read_logo(self, identity, id_):
        """Read the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "read", record=record)
        logo_file = record.files.get("logo")
        if logo_file is None:
            raise FileNotFoundError()
        return self.files.file_result_item(
            self.files,
            identity,
            logo_file,
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    @unit_of_work()
    def update_logo(self, identity, id_, stream, content_length=None, uow=None):
        """Update the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "update", record=record)

        logo_size_limit = 10**6
        max_size = current_app.config["COMMUNITIES_LOGO_MAX_FILE_SIZE"]
        if type(max_size) is int and max_size > 0:
            logo_size_limit = max_size

        if content_length > logo_size_limit:
            raise LogoSizeLimitError(logo_size_limit, content_length)

        record.files["logo"] = stream
        uow.register(RecordCommitOp(record))

        return self.files.file_result_item(
            self.files,
            identity,
            record.files["logo"],
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    @unit_of_work()
    def delete_logo(self, identity, id_, uow=None):
        """Delete the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        # update permission on community is required to be able to remove logo.
        self.require_permission(identity, "update", record=record)
        deleted_file = record.files.pop("logo", None)
        if deleted_file is None:
            raise FileNotFoundError()

        uow.register(RecordCommitOp(record))

        return self.files.file_result_item(
            self.files,
            identity,
            deleted_file,
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    def _get_featured_entry(self, raise_error=True, **kwargs):
        """Retrieve featured entry based on provided arguments."""
        errors = []
        try:
            featured_entry = CommunityFeatured.query.filter_by(**kwargs).one()
        except NoResultFound as e:
            if raise_error:
                raise CommunityFeaturedEntryDoesNotExistError(kwargs)
            featured_entry = None
            errors.append(str(e))

        return featured_entry, errors

    def featured_search(self, identity, params=None, es_preference=None, **kwargs):
        """Search featured communities."""
        self.require_permission(identity, "search")

        # Prepare and execute the search
        params = params or {}
        params["sort"] = "featured"

        search_results = self._search(
            "search",
            identity,
            params,
            es_preference,
            extra_filter=Bool(
                "must",
                must=[
                    Q("match", **{"access.visibility": "public"}),
                    Q("exists", **{"field": "featured.past"}),
                ],
            ),
            permission_action="featured_search",
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_results,
            params=params,
            links_tpl=LinksTemplate(
                self.config.links_featured_search, context={"args": params}
            ),
            links_item_tpl=self.links_item_tpl,
        )

    def featured_list(self, identity, community_id):
        """List featured entries for a community."""
        record = self.record_cls.pid.resolve(community_id)

        # Permissions
        self.require_permission(identity, "featured_list", record=record)

        featured_entries = CommunityFeatured.query.filter(
            CommunityFeatured.community_id == record.id,
        ).paginate(
            per_page=1000,
        )

        return self.config.result_list_cls_featured(
            self,
            identity,
            featured_entries,
            schema=self.schema_featured,
        )

    @unit_of_work()
    def featured_create(
        self, identity, community_id, data, raise_errors=True, uow=None
    ):
        """Create a featured entry for a community."""
        record = self.record_cls.pid.resolve(community_id)

        # Permissions
        self.require_permission(identity, "featured_create", record=record)

        data, errors = self.schema_featured.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        featured_entry = CommunityFeatured(**data)
        featured_entry.community_id = record.id

        # Run components
        self.run_components(
            "featured_create", identity, data=data, record=record, uow=uow
        )

        uow.register(CommunityFeaturedCommitOp(featured_entry))
        uow.register(RecordIndexOp(record, indexer=self.indexer, index_refresh=True))

        return self.result_item(
            self,
            identity,
            featured_entry,
            schema=self.schema_featured,
        )

    @unit_of_work()
    def featured_update(
        self, identity, community_id, data, featured_id, raise_errors=True, uow=None
    ):
        """Update a featured entry for a community."""
        record = self.record_cls.pid.resolve(community_id)
        featured_entry, _ = self._get_featured_entry(
            id=featured_id,
            community_id=record.id,
        )

        self.require_permission(identity, "featured_update", record=record)

        valid_data, errors = self.schema_featured.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        # Run components
        self.run_components(
            "featured_update", identity, data=valid_data, record=record, uow=uow
        )

        for key, value in valid_data.items():
            setattr(featured_entry, key, value)

        uow.register(CommunityFeaturedCommitOp(featured_entry))
        uow.register(RecordIndexOp(record, indexer=self.indexer, index_refresh=True))

        return self.result_item(
            self,
            identity,
            featured_entry,
            schema=self.schema_featured,
        )

    @unit_of_work()
    def featured_delete(
        self, identity, community_id, featured_id, raise_errors=True, uow=None
    ):
        """Delete a featured entry for a community."""
        record = self.record_cls.pid.resolve(community_id)
        featured_entry, _ = self._get_featured_entry(
            id=featured_id,
            community_id=record.id,
        )

        self.require_permission(identity, "featured_delete", record=record)

        # Run components
        self.run_components(
            "featured_delete", identity, data=None, record=record, uow=uow
        )

        uow.register(CommunityFeaturedDeleteOp(featured_entry))
        uow.register(RecordIndexOp(record, indexer=self.indexer, index_refresh=True))

        return

    #
    # notification handlers
    #
    def on_relation_update(self, identity, record_type, records_info, notif_time):
        """Relation updates notification handler."""
        if self.members:
            self.members.on_relation_update(
                identity, record_type, records_info, notif_time
            )
        if self.invitations:
            self.invitations.on_relation_update(
                identity, record_type, records_info, notif_time
            )

        return True
