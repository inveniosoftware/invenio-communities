# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community permissions."""

from invenio_administration.generators import Administration
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    Disable,
    IfConfig,
    SystemProcess,
)
from invenio_records_permissions.policies import BasePermissionPolicy
from invenio_users_resources.services.generators import GroupsEnabled
from invenio_users_resources.services.permissions import UserManager

from .generators import (
    AllowedMemberTypes,
    AuthenticatedButNotCommunityMembers,
    CommunityCurators,
    CommunityManagers,
    CommunityManagersForRole,
    CommunityMembers,
    CommunityOwners,
    CommunitySelfMember,
    IfCommunityDeleted,
    IfMemberPolicyClosed,
    IfRecordSubmissionPolicyClosed,
    IfRestricted,
    ReviewPolicy,
)


# Permission Policy
class CommunityPermissionPolicy(BasePermissionPolicy):
    """Permissions for Community CRUD operations."""

    # Community
    can_create = [AuthenticatedUser(), SystemProcess()]

    can_read = [
        IfRestricted("visibility", then_=[CommunityMembers()], else_=[AnyUser()]),
        SystemProcess(),
    ]

    # Used for search filtering of deleted records
    # cannot be implemented inside can_read - otherwise permission will
    # kick in before tombstone renders
    can_read_deleted = [
        IfCommunityDeleted(then_=[UserManager, SystemProcess()], else_=can_read)
    ]

    can_update = [CommunityOwners(), SystemProcess()]

    can_delete = [CommunityOwners(), SystemProcess()]

    can_purge = [CommunityOwners(), SystemProcess()]

    can_manage_access = [
        IfConfig("COMMUNITIES_ALLOW_RESTRICTED", then_=can_update, else_=[]),
    ]

    can_create_restricted = [
        IfConfig("COMMUNITIES_ALLOW_RESTRICTED", then_=can_create, else_=[]),
    ]

    can_search = [AnyUser(), SystemProcess()]

    can_search_user_communities = [AuthenticatedUser(), SystemProcess()]

    can_search_invites = [CommunityManagers(), SystemProcess()]

    can_search_requests = [CommunityManagers(), CommunityCurators(), SystemProcess()]

    can_rename = [CommunityOwners(), SystemProcess()]

    can_submit_record = [
        IfRecordSubmissionPolicyClosed(
            then_=[CommunityMembers(), SystemProcess()],
            else_=[
                IfRestricted(
                    "visibility",
                    then_=[CommunityMembers()],
                    else_=[AuthenticatedUser()],
                ),
            ],
        ),
    ]

    # who can include a record directly, without a review
    can_include_directly = [
        ReviewPolicy(
            closed_=[Disable()],
            open_=[CommunityCurators()],
            members_=[CommunityMembers()],
        )
    ]

    can_members_add = [
        CommunityManagersForRole(),
        AllowedMemberTypes("group"),
        GroupsEnabled("group"),
        SystemProcess(),
    ]

    can_members_invite = [
        CommunityManagersForRole(),
        AllowedMemberTypes("user", "email"),
        SystemProcess(),
    ]

    can_members_manage = [
        CommunityManagers(),
        SystemProcess(),
    ]

    can_members_search = [
        CommunityMembers(),
        SystemProcess(),
    ]

    can_members_search_public = [
        IfRestricted(
            "visibility",
            then_=[CommunityMembers()],
            else_=[
                IfRestricted(
                    "members_visibility",
                    then_=[CommunityMembers()],
                    else_=[AnyUser()],
                ),
            ],
        ),
        SystemProcess(),
    ]

    # Ability to use membership update api
    can_members_bulk_update = [
        CommunityMembers(),
        SystemProcess(),
    ]

    can_members_bulk_delete = can_members_bulk_update

    # Ability to update a single membership
    can_members_update = [
        CommunityManagersForRole(),
        CommunitySelfMember(),
        SystemProcess(),
    ]

    # Ability to delete a single membership
    can_members_delete = can_members_update

    can_invite_owners = [CommunityOwners(), SystemProcess()]

    # Abilities for featured communities
    can_featured_search = [AnyUser(), SystemProcess()]
    can_featured_list = [Administration(), SystemProcess()]
    can_featured_create = [Administration(), SystemProcess()]
    can_featured_update = [Administration(), SystemProcess()]
    can_featured_delete = [Administration(), SystemProcess()]

    # Used to hide at the moment the `is_verified` field. It should be set to
    # correct permissions based on which the field will be exposed only to moderators
    can_moderate = [Disable()]

    # Permissions to crud community theming
    can_set_theme = [SystemProcess()]
    can_delete_theme = can_set_theme

    # Permissions to set if communities can have children
    can_manage_children = [SystemProcess()]

    # Permission for assigning a parent community
    can_manage_parent = [Administration(), SystemProcess()]

    # request_membership permission is based on configuration, community settings and
    # identity. Other factors (e.g., previous membership requests) are not under
    # its purview and are dealt with elsewhere.
    can_request_membership = [
        IfConfig(
            "COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS",
            then_=[
                IfMemberPolicyClosed(
                    then_=[Disable()],
                    else_=[AuthenticatedButNotCommunityMembers()],
                ),
            ],
            else_=[Disable()],
        ),
    ]


def can_perform_action(community, context):
    """Check if the given action is available on the request."""
    action = context.get("action")
    identity = context.get("identity")
    permission_policy_cls = context.get("permission_policy_cls")
    permission = permission_policy_cls(action, community=community)
    return permission.allows(identity)
