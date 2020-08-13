# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for Invenio RDM Records."""
from collections import namedtuple
from functools import partial

from flask_principal import UserNeed
from invenio_access.permissions import any_user
from invenio_records_permissions.generators import Generator
from invenio_records_permissions.policies import BasePermissionPolicy

_CommunityMemberNeed = namedtuple(
    'CommunityMemberNeed', ['method', 'community', 'role'])
CommunityMemberNeed = partial(_CommunityMemberNeed, "community_member")


class CommunityMember(Generator):
    """Generator for community member need."""

    def __init__(self, roles):
        """."""
        self.roles = roles

    def needs(self, comid=None, **kwargs):
        """Returns community member need."""
        return [CommunityMemberNeed(comid.id, r) for r in self.roles]


class CommunityMembershipOwner(Generator):

    def needs(self, community_member=None, **kwargs):
        """Returns community member need."""
        if community_member.user_id:
            return [UserNeed(community_member.user_id)]
        return []


class AnyUserIfUnresolvedInvite(Generator):

    def needs(self, community_member=None, **kwargs):
        """Skip check at this stage if the membership is an invitation."""
        if community_member.request.is_invite:
            return [any_user]
        return []


class CommunityMemberIfRequest(Generator):

    def __init__(self, roles):
        self.roles = roles

    def needs(self, comid=None, community_member=None, **kwargs):
        """If its a request only defined community roles can handle it."""
        if not community_member.request.is_invite:
            return [CommunityMemberNeed(comid.id, r) for r in self.roles]
        return []


class AnyUserIfOpenMemberPolicy(Generator):

    def needs(self, community=None, **kwargs):
        """If the member policy is open then anyone can request to join."""
        if community['member_policy'] == 'open':
            return [any_user]
        return []


class CommunityMemberPermissionPolicy(BasePermissionPolicy):
    """Permission policy for member functionality."""
    can_create_membership = [
        CommunityMember(['admin']),
        AnyUserIfOpenMemberPolicy()
    ]
    can_list_accepted_members = [CommunityMember(['admin', 'curator', 'member'])]
    can_list_pending_members = [CommunityMember(['admin'])]
    can_list_rejected_members = [CommunityMember(['admin'])]
    can_list_all_members = [CommunityMember(['admin'])]

    can_modify_membership = [CommunityMember(['admin'])]

    can_delete_membership = [
        CommunityMember(['admin']),
        CommunityMembershipOwner(),
    ]

    can_handle_request = [
        AnyUserIfUnresolvedInvite(),
        CommunityMemberIfRequest(['admin']),
    ]

    can_get_membership = [
        CommunityMemberIfRequest(['admin']),
        CommunityMembershipOwner(),
        AnyUserIfUnresolvedInvite()
    ]



def is_permitted_action(action, **kwargs):
    """Helper function to apply a permission check."""
    return CommunityMemberPermissionPolicy(
        action=action, **kwargs).can()
