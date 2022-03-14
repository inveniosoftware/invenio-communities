# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community permissions."""

from invenio_records_permissions.generators import AnyUser, \
    AuthenticatedUser, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy

from .generators import CommunityOwners, IfPolicyClosed, IfRestricted

# Permission Policy

class CommunityPermissionPolicy(BasePermissionPolicy):
    """Permissions for Community CRUD operations."""

    # Community
    can_create = [AuthenticatedUser(), SystemProcess()]

    can_read = [
        IfRestricted(
            'visibility',
            then_=[CommunityOwners()],
            else_=[AnyUser()]),
        ]

    can_update = [CommunityOwners(), SystemProcess()]

    can_delete = [CommunityOwners(), SystemProcess()]

    can_search = [AnyUser(), SystemProcess()]

    can_search_user_communities = [AuthenticatedUser(), SystemProcess()]

    can_rename = [CommunityOwners(), SystemProcess()]

    can_submit_record = [
        IfPolicyClosed(
            'record_policy',
            then_=[CommunityOwners(), SystemProcess()],
            else_=[IfRestricted(
                'visibility',
                then_=[CommunityOwners()],
                else_=[AuthenticatedUser()]),
            ],
        ),
    ]

    # Placed here because passed record is a community

    # can_create_member = [CommunityOwners(), SystemProcess()]

    # can_search_members = [
    #     SystemProcess(),
    #     IfRestricted(
    #         'visibility',
    #         then_=[CommunityOwners()],
    #         else_=[AnyUser()]
    #     ),
    # ]

    # Members (passed record is a member)

    # This is a new performance enhancing permission to be used when reading
    # a record from the search results.
    # Because can_search_members has already been applied, any user who got
    # through can read the record.
    # can_read_search_members = [AnyUser(), SystemProcess()]
    # can_read_member = [
    #     IfCommunityRestricted(
    #         then_=[AnyMember()],
    #         else_=[AnyUser()]
    #     ),
    # ]
    # can_update_member = [SelfMember(), OwnerMember(), ManagerMember()]
    # can_delete_member = [SelfMember(), OwnerMember(), ManagerMember()]
