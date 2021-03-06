# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community permissions."""

from flask_principal import UserNeed
from flask_security import current_user
from invenio_access.permissions import any_user
from invenio_records_permissions.generators import Generator
from invenio_records_permissions.policies import BasePermissionPolicy

from invenio_communities.members.permissions import CommunityMember


class CommunityVisibilityPolicy(Generator):
    """Allows only community members to read the community if its hidden."""

    def needs(self, community=None, **kwargs):
        """."""
        if community['visibility'] == 'public':
            return [any_user]
        else:
            return [CommunityMember(['admin', 'curator', 'member'])]


class CommunityOwner(Generator):
    """Returns community owner need."""

    def needs(self, community=None, **kwargs):
        """."""
        return [UserNeed(community['created_by'])]


class CommunityPermissionPolicy(BasePermissionPolicy):
    """Permissions for Community CRUD operations."""

    can_read_community = [
        CommunityVisibilityPolicy(),
    ]

    can_update_community = [
        CommunityMember(['admin', 'curator']),
    ]
    can_delete_community = [
        CommunityMember(['admin']),
    ]


def allow_logged_in(*args, **kwargs):
    """Permission that allows only logged in users to perform the operation."""
    def can(self):
        """."""
        return current_user.is_authenticated
    return type('AllowCommunityOwner', (), {'can': can})()


def can_read_community(record, *args, **kwargs):
    """Permission wrapper."""
    def can(self):
        """."""
        return CommunityPermissionPolicy(
            action='read_community',
            comid=record.pid,
            community=record,
        ).can()
    return type('AllowCommunityOwner', (), {'can': can})()


def can_update_community(record, *args, **kwargs):
    """Permission wrapper."""
    def can(self):
        """."""
        return CommunityPermissionPolicy(
            action='update_community',
            comid=record.pid,
            community=record,
        ).can()
    return type('AllowCommunityOwner', (), {'can': can})()


def can_delete_community(record, *args, **kwargs):
    """Permission wrapper."""
    def can(self):
        """."""
        return CommunityPermissionPolicy(
            action='delete_community',
            comid=record.pid,
            community=record,
        ).can()
    return type('AllowCommunityOwner', (), {'can': can})()
