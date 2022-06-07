# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community permissions."""

from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    Disable,
    SystemProcess,
)
from invenio_records_permissions.policies import BasePermissionPolicy

from .generators import (
    AllowedMemberTypes,
    CommunityCurators,
    CommunityManagers,
    CommunityManagersForRole,
    CommunityMembers,
    CommunityOwners,
    CommunitySelfMember,
    GroupsEnabled,
    IfPolicyClosed,
    IfRestricted,
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

    can_update = [CommunityOwners(), SystemProcess()]

    can_delete = [CommunityOwners(), SystemProcess()]

    can_search = [AnyUser(), SystemProcess()]

    can_search_user_communities = [AuthenticatedUser(), SystemProcess()]

    can_search_invites = [CommunityManagers(), SystemProcess()]

    can_search_requests = [CommunityManagers(), CommunityCurators(), SystemProcess()]

    can_rename = [CommunityOwners(), SystemProcess()]

    can_submit_record = [
        IfPolicyClosed(
            "record_policy",
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
        IfRestricted("visibility", then_=[CommunityMembers()], else_=[AnyUser()]),
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
    can_featured_list = [SystemProcess()]
    can_featured_create = [SystemProcess()]
    can_featured_update = [SystemProcess()]
    can_featured_delete = [SystemProcess()]
