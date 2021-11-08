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

import operator
from functools import reduce
from itertools import chain

from elasticsearch_dsl.query import Q
from flask_principal import UserNeed
from invenio_access.permissions import any_user
from invenio_records_permissions.generators import AnyUser, \
    AuthenticatedUser, Generator, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy


# TODO: Move class to Invenio-Records-Permissions and make more reusable ()
class IfRestrictedBase(Generator):
    """IfRestricted generator.

    IfRestricted(
        'record',
        then_=[RecordPermissionLevel('view')],
        else_=[ActionNeed(superuser-access)],
    )
    """

    def __init__(self, field, then_, else_):
        """Constructor."""
        self.field = field
        self.then_ = then_
        self.else_ = else_

    def generators(self, record):
        """Get the "then" or "else" generators."""
        if record is None:
            # TODO - when permissions on links are checked, the record is not
            # passes properly, causing below ``record.access`` to fail.
            return self.else_
        # TODO: Next statement should be made more reusable
        is_restricted = getattr(
            record.access.protection, self.field, "restricted")
        return self.then_ if is_restricted == "restricted" else self.else_

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        needs = [
            g.needs(record=record, **kwargs) for g in self.generators(record)]
        return set(chain.from_iterable(needs))

    def excludes(self, record=None, **kwargs):
        """Set of Needs denying permission."""
        needs = [
            g.excludes(record=record, **kwargs) for g in self.generators(
                record)]
        return set(chain.from_iterable(needs))

    def make_query(self, generators, **kwargs):
        """Make a query for one set of generators."""
        queries = [g.query_filter(**kwargs) for g in generators]
        queries = [q for q in queries if q]
        return reduce(operator.or_, queries) if queries else None

    def query_filter(self, **kwargs):
        """Filters for current identity as super user."""
        # TODO: Next two statement should be made more reusable
        q_restricted = Q("match", **{f"access.{self.field}": "restricted"})
        q_public = Q("match", **{f"access.{self.field}": "public"})
        then_query = self.make_query(self.then_, **kwargs)
        else_query = self.make_query(self.else_, **kwargs)

        if then_query and else_query:
            return (q_restricted & then_query) | (q_public & else_query)
        elif then_query:
            return (q_restricted & then_query) | q_public
        elif else_query:
            return q_public & else_query
        else:
            return q_public


# TODO: Remove class once IfRestrictedBase has been moved.
class IfRestricted(IfRestrictedBase):
    """IfRestricted."""

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
