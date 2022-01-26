# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitations Service API."""

from copy import deepcopy

from elasticsearch_dsl.query import Q
from flask_babelex import gettext as _
from invenio_records_resources.services import RecordService
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests import current_registry, current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_requests.services.requests.links import RequestLinksTemplate
from marshmallow import ValidationError

from ...communities.records.api import Community
from ...permissions import CommunityRoleManager
from ...proxies import current_communities
from ...members import AlreadyMemberError
from ..errors import AlreadyInvitedError
from .request_types import CommunityMemberInvitation

class InvitationService(RecordService):
    """Invitation Service.

    In an Invitation Request, the
    topic               ---- community
    creator/created_by  ---- community
    receiver            ---- invited user
    """

    @unit_of_work()
    def create(self, identity, data, uow=None):
        """Create invitation."""
        data = deepcopy(data)
        community_dict = data.pop('topic', None)
        entity_dict = data.pop('receiver', None)

        community = ResolverRegistry.resolve_entity_proxy(
            community_dict).resolve()

        # Could be just hardcoded and not passed as an argument
        type_ = current_registry.lookup(data.pop('type', None))

        entity = ResolverRegistry.resolve_entity_proxy(
            entity_dict).resolve()

        role = data.get("payload", {}).get("role")
        self._assert_can_invite(identity, community, entity_dict, role)

        # inject title
        # TODO: translate
        community_title = community.metadata["title"]
        data["title"] = f"Invitation to join \"{community_title}\" as {role}"

        request_item = current_requests_service.create(
            identity,
            data,
            request_type=type_,
            receiver=entity,
            creator=community,
            topic=community,
            permission_args={"record": community},
            uow=uow,
        )
        return self._to_invitation_item(
            identity, request_item, community.pid.pid_value
        )

    def _assert_can_invite(self, identity, community, entity_dict, role):
        """Raises if can't invite."""
        user_id = str(entity_dict.get("user"))
        community_uuid = str(community.id)

        # Can't invite if already invited
        search = current_requests_service._search(
            'search',
            identity,
            params={},
            es_preference=None,
            permission_action='read',
            extra_filter=(
                # TODO Make flexible for group
                Q('term', **{"receiver.user": user_id}) &
                Q('term', **{"topic.community": community_uuid}) &
                Q('term', is_open=True) &
                Q('term', type=CommunityMemberInvitation.type_id)
            )
        )
        results = search.execute()
        if any(results):
            raise AlreadyInvitedError

        # Can't invite if already member
        members_service = current_communities.service.members
        if members_service.is_member(community_uuid, user_id):
            raise AlreadyMemberError

        # Can't invite owner if identity is not owner
        self._assert_identity_owner_if_role_owner(
            identity, community_uuid, role
        )

    def _assert_identity_owner_if_role_owner(
            self, identity, community_uuid, role):
        if role == "owner":
            community_roles = [
                CommunityRoleManager.from_need(n)
                for n in identity.provides
                if CommunityRoleManager.check_need(n)
            ]
            is_owner = any((
                cr for cr in community_roles
                if cr.role == "owner" and cr.community_uuid == community_uuid
            ))

            if not is_owner:
                raise PermissionDeniedError

    def read(self, identity, community_id, id_):
        """Retrieve a record."""
        request_item = current_requests_service.read(
            identity,
            id_,
        )
        return self._to_invitation_item(
            identity, request_item, community_id
        )

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None):
        """Update invitation."""
        self._assert_only_payload_can_be_updated(id_, data)

        community_dict = data.get('topic')
        community = ResolverRegistry.resolve_entity_proxy(
            community_dict
        ).resolve()
        community_uuid = str(community.id)
        role = data.get("payload", {}).get("role")
        self._assert_identity_owner_if_role_owner(
            identity, community_uuid, role
        )

        request_item = current_requests_service.update(
            identity,
            id_,
            data,
            revision_id=revision_id,
            uow=uow,
        )
        return self._to_invitation_item(
            identity, request_item, community.pid.pid_value
        )

    def _assert_only_payload_can_be_updated(self, id_, data):
        """Only payload can be updated."""
        # If this is common perhaps have this kind of check be done in
        # invenio-requests
        allow_update = ["payload"]
        request = current_requests_service.record_cls.get_record(id_)
        schema = request.type.marshmallow_schema()
        immutable_field_names = [
            fn for (fn, f) in schema().fields.items()
            if not f.dump_only and fn not in allow_update
        ]
        # If these fields are passed a different value, it's an error
        for field_name in immutable_field_names:
            # Have to stringify to overcome differences of type (e.g. str
            # versus UUID object)
            incoming_data = str(data.get(field_name))
            present_data = str(
                # getattr to account for id (and other fields like it)
                request.get(field_name) or getattr(request, field_name, None)
            )
            if incoming_data != present_data:
                raise ValidationError(
                    message=_("This field can't be updated."),
                    field_name=field_name
                )

    @unit_of_work()
    def execute_action(
            self, identity, community_id, id_, action, data=None,
            uow=None):
        """Execute action."""
        request_item = current_requests_service.execute_action(
            identity,
            id_,
            action,
            data=data,
            uow=uow
        )
        return self._to_invitation_item(identity, request_item, community_id)

    def search(self, identity, community_id, params=None, es_preference=None,
               **kwargs):
        """Search for invitation-requests matching the querystring."""
        self.require_permission(identity, 'search')

        community = Community.pid.resolve(community_id)
        community_uuid = str(community.id)

        # Prepare and execute the search
        params = params or {}
        search = current_requests_service._search(
            'search',
            identity,
            params=params,
            es_preference=es_preference,
            permission_action='read',
            extra_filter=(
                Q('term', type=CommunityMemberInvitation.type_id) &
                Q('term', **{"topic.community": community_uuid})
            )
        )
        results = search.execute()

        return self.result_list(
            current_requests_service,
            identity,
            results,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search,
                context={
                    "args": params,
                    "community_id": community_id,
                }
            ),
            links_item_tpl=RequestLinksTemplate(
                current_requests_service.config.links_item,
                current_requests_service.config.action_link
            ),
        )

    def _to_invitation_item(self, identity, request_item, community_id):
        """Convert request item to invitation item.

        We want to override the links, so we re-wrap the result item.
        """
        invitation_item = self.result_item(
            current_requests_service,
            identity,
            request=request_item._request,
            errors=request_item._errors,
            links_tpl=RequestLinksTemplate(
                self.config.links_item,
                self.config.action_link,
                context={"community_id": community_id}
            ),
            schema=request_item._schema,
        )
        return invitation_item
