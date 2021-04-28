# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community permissions."""

from elasticsearch_dsl.query import Q
from flask_principal import UserNeed
from invenio_access.permissions import any_user
from invenio_rdm_records.services.generators import \
    IfRestricted as IfRestrictedBase
from invenio_records_permissions.generators import AnyUser, \
    AuthenticatedUser, Generator, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy


class IfRestricted(IfRestrictedBase):
    """IfRestricted.

    IfRestricted(
        'record',
        then_=[RecordPermissionLevel('view')],
        else_=[ActionNeed(superuser-access)],
    )

    A record permission level defines an aggregated set of
    low-level permissions,
    that grants increasing level of permissions to a record.

    """

    def generators(self, record):
        """Get the "then" or "else" generators."""
        if record is None:
            # TODO - when permissions on links are checked, the record is not
            # passes properly, causing below ``record.access`` to fail.
            return self.else_
        is_restricted = getattr(
            record.access, self.field, "restricted")
        return self.then_ if is_restricted == "restricted" else self.else_


class CommunityOwners(Generator):
    """Allows community owners."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        if record:
            return [
                UserNeed(owner.owner_id)
                for owner in record.access.owned_by
                ]
        else:
            return [any_user]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        users = [n.value for n in identity.provides if n.method == "id"]
        return Q(
            "terms",
            **{"access.owned_by.user": users}
            )


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
