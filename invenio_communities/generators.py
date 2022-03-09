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

import operator
from collections import namedtuple
from functools import partial, reduce
from itertools import chain

from elasticsearch_dsl.query import Q
from flask_principal import UserNeed
from invenio_access.permissions import any_user
from invenio_records_permissions.generators import Generator

_Need = namedtuple('Need', ['method', 'value', 'role'])

CommunityRoleNeed = partial(_Need, 'community')
"""Defines a need for a community role.

You can create a community role need like below:

.. code-block:: python

    need = CommunityRoleNeed(community.id, 'manager')
    # Community role needs can be identified by their method attribute
    assert need.method == 'community
    # The community identifier can be accessed via the value attribute
    assert need.value == community.id
    # The role held within the community can be accessed via the role attribute
    assert need.role == 'manager
"""


# TODO: Move class to Invenio-Records-Permissions and make more reusable
class IfRestrictedBase(Generator):
    """IfRestricted generator.

    IfRestricted(
        'record', 'restricted', 'public'
        then_=[RecordPermissionLevel('view')],
        else_=[ActionNeed(superuser-access)],
    )
    """

    def __init__(self, field_getter,
                 field_name, then_value, else_value, then_, else_):
        """Constructor."""
        self.field_getter = field_getter
        self.field_name = field_name
        self.then_value = then_value
        self.else_value = else_value
        self.then_ = then_
        self.else_ = else_

    def generators(self, record):
        """Get the "then" or "else" generators."""
        if record is None:
            # TODO - when permissions on links are checked, the record is not
            # passes properly, causing below ``record.access`` to fail.
            return self.else_
        # TODO: Next statement should be made more reusable
        is_then_value = self.field_getter(record) or self.then_value
        return self.then_ if is_then_value == self.then_value else self.else_

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
        """Filters for current identity."""
        # TODO: Next two statement should be made more reusable
        q_then = Q("match", **{self.field_name: self.then_value})
        q_else = Q("match", **{self.field_name: self.else_value})
        then_query = self.make_query(self.then_, **kwargs)
        else_query = self.make_query(self.else_, **kwargs)

        if then_query and else_query:
            return (q_then & then_query) | (q_else & else_query)
        elif then_query:
            return (q_then & then_query) | q_else
        elif else_query:
            return q_else & else_query
        else:
            return q_else


# TODO: Remove class once IfRestrictedBase has been moved.
class IfRestricted(IfRestrictedBase):
    """IfRestricted."""

    def __init__(self, field, then_, else_):
        """Initialize."""
        super().__init__(
            lambda r: getattr(r.access, field, None),
            f"access.{field}",
            "restricted",
            "public",
            then_,
            else_,
        )


class IfPolicyClosed(IfRestrictedBase):
    """If policy is closed."""

    def __init__(self, field, then_, else_):
        """Initialize."""
        super().__init__(
            lambda r: getattr(r.access, field, None),
            f"access.{field}",
            "open",
            "closed",
            then_,
            else_,
        )


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
