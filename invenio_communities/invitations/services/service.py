# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitations Service API."""

from copy import deepcopy

from elasticsearch_dsl.query import Q
from invenio_records_resources.services import RecordService
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests import current_registry, current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry

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

        type_ = current_registry.lookup(data.pop('type', None))

        entity = ResolverRegistry.resolve_entity_proxy(
            entity_dict).resolve()

        role = data.get("payload", {}).get("role")
        self._assert_can_invite(identity, community, entity_dict, role)

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

        return request_item

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

    @unit_of_work()
    def update(self, identity, id_, data, uow=None):
        """Update invitation."""
        community_dict = data.get('topic')
        entity_dict = data.get('receiver')
        community = ResolverRegistry.resolve_entity_proxy(
            community_dict).resolve()

        role = data.get("payload", {}).get("role")
        self._assert_can_invite(identity, community, entity_dict, role)

        request_item = current_requests_service.update(
            identity,
            id_,
            data,
            uow=uow,
        )

        return request_item
