# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitation request type permission policy."""

from elasticsearch_dsl.query import Q
from flask_principal import UserNeed
from invenio_records_permissions.generators import Generator, SystemProcess
from invenio_requests.customizations.base import BaseRequestPermissionPolicy

from ...permissions import CommunityOwner, CommunityManager, \
    CommunityRoleManager, create_community_role_need
from .common import REQUEST_TYPE_ID

# Invitation Generators

class InvitationCommunityOwner(Generator):
    """Allows owner of the community of the invitation."""

    def needs(self, request=None, **kwargs):
        """Enabling Needs.

        :param record: an invitation
        """
        invitation = request

        # Symptom of how api.py objects are falsey if dict empty
        if invitation is None:
            return []

        # Topic contains the community
        community_uuid = invitation["topic"]["community"]
        return [create_community_role_need(community_uuid, "owner")]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        community_uuids = [
            CommunityRoleManager.from_need(n).community_uuid
            for n in identity.provides
            if (
                n.method == "role" and
                CommunityRoleManager.check_string(n.value) and
                CommunityRoleManager.from_need(n).role == "owner"
            )
        ]

        return (
            Q("term", type=REQUEST_TYPE_ID) &
            Q("terms", **{"topic.community": community_uuids})
        )


class InvitationCommunityManager(Generator):
    """Allows manager of the community of the invitation."""

    def needs(self, request=None, **kwargs):
        """Enabling Needs.

        :param request: an invitation
        """
        invitation = request

        # Symptom of how api.py objects are falsey if dict empty
        if invitation is None:
            return []

        community_uuid = invitation["topic"]["community"]
        return [create_community_role_need(community_uuid, "manager")]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        community_uuids = [
            CommunityRoleManager.from_need(n).community_uuid
            for n in identity.provides
            if (
                CommunityRoleManager.check_need(n) and
                CommunityRoleManager.from_need(n).role == "manager"
            )
        ]

        return (
            Q("term", type=REQUEST_TYPE_ID) &
            Q("terms", **{"topic.community": community_uuids})
        )


class InvitationInvitee(Generator):
    """Allows invited entity of the invitation."""

    def needs(self, request=None, **kwargs):
        """Enabling Needs.

        :param request: an invitation
        """
        invitation = request

        # Symptom of how api.py objects are falsey if dict empty
        if invitation is None:
            return []

        receiver = invitation["receiver"]
        # TODO: add group
        user_id = int(receiver.get("user"))
        return [UserNeed(user_id)]


class InvitationPermissionPolicy(BaseRequestPermissionPolicy):
    """Invitation permission policy."""

    # Passed record is a community
    can_create = [
        CommunityOwner(), CommunityManager(), SystemProcess()
    ]

    # Passed record is an invitation
    can_read = [
        InvitationCommunityOwner(), InvitationCommunityManager(),
        InvitationInvitee(), SystemProcess()
    ]
    can_update = [
        InvitationCommunityOwner(), InvitationCommunityManager(),
        SystemProcess()
    ]
    can_action_cancel = [
        InvitationCommunityOwner(), InvitationCommunityManager(),
        SystemProcess()
    ]
    can_action_accept = [InvitationInvitee(), SystemProcess()]
    can_action_decline = [InvitationInvitee(), SystemProcess()]

    # Comments (passed record is a request event)
    # TODO
    # can_comment = [
    #     InvitationCommunityOwner(), InvitationCommunityManager(),
    #     InvitationInvitee(), SystemProcess()
    # ]
