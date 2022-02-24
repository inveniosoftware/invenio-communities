# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.

#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community permissions."""

from invenio_records_permissions.generators import AnyUser, \
    AuthenticatedUser, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy

from ...generators import CommunityOwners, IfPolicyClosed, IfRestricted


class CommunityPermissionPolicy(BasePermissionPolicy):
    """Permissions for Community CRUD operations."""

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
