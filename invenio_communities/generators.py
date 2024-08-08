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

import operator
from collections import namedtuple
from functools import partial, reduce
from itertools import chain

from flask_principal import UserNeed
from invenio_access.permissions import any_user, authenticated_user, system_process
from invenio_records.dictutils import dict_lookup
from invenio_records_permissions.generators import Generator
from invenio_search.engine import dsl

from .communities.records.systemfields.deletion_status import (
    CommunityDeletionStatusEnum,
)
from .proxies import current_roles

_Need = namedtuple("Need", ["method", "value", "role"])

CommunityRoleNeed = partial(_Need, "community")
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

    def __init__(self, field_getter, field_name, then_value, else_value, then_, else_):
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
        needs = [g.needs(record=record, **kwargs) for g in self.generators(record)]
        return set(chain.from_iterable(needs))

    def excludes(self, record=None, **kwargs):
        """Set of Needs denying permission."""
        needs = [g.excludes(record=record, **kwargs) for g in self.generators(record)]
        return set(chain.from_iterable(needs))

    def make_query(self, generators, **kwargs):
        """Make a query for one set of generators."""
        queries = [g.query_filter(**kwargs) for g in generators]
        queries = [q for q in queries if q]
        return reduce(operator.or_, queries) if queries else None

    def query_filter(self, **kwargs):
        """Filters for current identity."""
        # TODO: Next two statement should be made more reusable
        q_then = dsl.Q("match", **{self.field_name: self.then_value})
        q_else = dsl.Q("match", **{self.field_name: self.else_value})
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
            lambda r: (
                getattr(r.access, field, None)
                if hasattr(r, "access")
                else r.get("access", {}).get(field)
            ),  # needed for running permission check at serialization time and avoid db query
            f"access.{field}",
            "restricted",
            "public",
            then_,
            else_,
        )


class ReviewPolicy(Generator):
    """If policy is closed."""

    def __init__(self, closed_, open_, members_):
        """Constructor."""
        self.closed_ = closed_
        self.open_ = open_
        self.members_ = members_

    def _generators(self, record, **kwargs):
        """Get the generators."""
        review_policy = dict_lookup(record, "access.review_policy")

        if review_policy == "closed":
            return self.closed_
        elif review_policy == "open":
            return self.open_
        elif review_policy == "members":
            return self.members_

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        needs = [
            g.needs(record=record, **kwargs) for g in self._generators(record, **kwargs)
        ]
        return set(chain.from_iterable(needs))

    def excludes(self, record=None, **kwargs):
        """Set of Needs denying permission."""
        needs = [
            g.excludes(record=record, **kwargs)
            for g in self._generators(record, **kwargs)
        ]
        return set(chain.from_iterable(needs))


class IfRecordSubmissionPolicyClosed(IfRestrictedBase):
    """If record submission policy is closed."""

    def __init__(self, then_, else_):
        """Initialize."""
        field = "record_submission_policy"
        super().__init__(
            field_getter=lambda r: (
                getattr(r.access, field, None)
                if hasattr(r, "access")
                else r.get("access", {}).get(field)
            ),  # needed for running permission check at serialization time and avoid db query
            field_name=f"access.{field}",
            then_value="closed",
            else_value="open",
            then_=then_,
            else_=else_,
        )


class IfMemberPolicyClosed(IfRestrictedBase):
    """If member policy is closed."""

    def __init__(self, then_, else_):
        """Initialize."""
        field = "member_policy"
        super().__init__(
            field_getter=lambda r: (
                getattr(r.access, field, None)
                if hasattr(r, "access")
                else r.get("access", {}).get(field)
            ),  # needed for running permission check at serialization time and avoid db query
            field_name=f"access.{field}",
            then_value="closed",
            else_value="open",
            then_=then_,
            else_=else_,
        )


class IfCommunityDeleted(Generator):
    """Conditional generator for deleted communities."""

    def __init__(self, then_, else_):
        """Constructor."""
        self.then_ = then_
        self.else_ = else_

    def generators(self, record):
        """Get the "then" or "else" generators."""
        if record is None:
            # if no records, we assume it returns standard else response
            return self.else_

        is_deleted = record.deletion_status.is_deleted
        return self.then_ if is_deleted else self.else_

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        needs = [g.needs(record=record, **kwargs) for g in self.generators(record)]
        return set(chain.from_iterable(needs))

    def excludes(self, record=None, **kwargs):
        """Set of Needs denying permission."""
        needs = [g.excludes(record=record, **kwargs) for g in self.generators(record)]
        return set(chain.from_iterable(needs))

    def make_query(self, generators, **kwargs):
        """Make a query for one set of generators."""
        queries = [g.query_filter(**kwargs) for g in generators]
        queries = [q for q in queries if q]
        return reduce(operator.or_, queries) if queries else None

    def query_filter(self, **kwargs):
        """Filters for current identity."""
        q_then = dsl.Q("match_all")
        q_else = dsl.Q(
            "term", **{"deletion_status": CommunityDeletionStatusEnum.PUBLISHED.value}
        )
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


#
# Community membership generators
#


class AuthenticatedButNotCommunityMembers(Generator):
    """Authenticated user not part of community."""

    def needs(self, record=None, **kwargs):
        """Required needs."""
        return [authenticated_user]

    def excludes(self, record=None, **kwargs):
        """Exluding needs.

        Excludes identities with a role in the community. This assumes all roles at
        this point mean valid memberships. This is the same assumption as
        `CommunityMembers` below.
        """
        if not record:
            return []
        community_id = str(record.id)
        return [CommunityRoleNeed(community_id, r.name) for r in current_roles]


class CommunityRoles(Generator):
    """Base class for community roles generators."""

    def roles(self, **kwargs):
        """R."""
        raise NotImplementedError

    def communities(self, identity):
        """Communities."""
        raise NotImplementedError

    def needs(self, record=None, community_id=None, **kwargs):
        """Enabling Needs."""
        if community_id is None:
            community_id = record.id

        assert community_id, "No community id provided."
        community_id = str(community_id)

        roles = self.roles(**kwargs)
        if roles:
            needs = [CommunityRoleNeed(community_id, role) for role in roles]
            return needs
        return []

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        # Gives access to all community members.
        return dsl.Q("terms", **{"_id": self.communities(identity)})


class CommunityMembers(CommunityRoles):
    """Roles representing all members of a community."""

    def roles(self, **kwargs):
        """Roles."""
        return [r.name for r in current_roles]

    def communities(self, identity):
        """Communities."""
        return [n.value for n in identity.provides if n.method == "community"]


class CommunityCurators(CommunityRoles):
    """Roles representing all curators of a community."""

    def roles(self, **kwargs):
        """Roles."""
        return [r.name for r in current_roles.can("curate")]


class CommunityManagers(CommunityRoles):
    """Roles representing all managers of a community."""

    def roles(self, **kwargs):
        """Roles."""
        return [r.name for r in current_roles.can("manage")]


class CommunityManagersForRole(CommunityRoles):
    """Roles representing all managers of a community for a role update."""

    def roles(self, role=None, member=None, **kwargs):
        """Roles."""
        allowed_roles = []
        if role is not None and member is not None:
            # Update from an old role to a new role. The most restrictive set
            # applies.
            new_allowed_roles = set(current_roles.manager_roles(role))
            old_allowed_roles = set(current_roles.manager_roles(member.role))
            allowed_roles = new_allowed_roles & old_allowed_roles
        elif role is not None:
            # Adding/inviting a new role
            allowed_roles = current_roles.manager_roles(role)
        elif member is not None:
            # Deleting or updating a member with a given role (without changing
            # role)
            allowed_roles = current_roles.manager_roles(member.role)
        else:
            raise NotImplementedError("You must provide a role and/or a member.")

        return [r.name for r in allowed_roles]


class CommunityOwners(CommunityRoles):
    """Roles representing the owners of a community."""

    def roles(self, **kwargs):
        """Roles."""
        return [current_roles.owner_role.name]

    def communities(self, identity):
        """Communities."""
        return [
            n.value
            for n in identity.provides
            if n.method == "community" and n.role == current_roles.owner_role.name
        ]


class CommunitySelfMember(Generator):
    """Allows a member themselves (only for users)."""

    def needs(self, member=None, **kwargs):
        """Enabling needs."""
        if member is not None and member.user_id is not None:
            return [UserNeed(member.user_id)]
        return []

    def query_filter(self, identity=None, **kwargs):
        """Not implemented."""
        raise NotImplementedError("Search permission not supported.")


#
# Business-level rules.
#
class AllowedMemberTypes(Generator):
    """Generator to restrict to set of allowed member types.

    We are restricting member types that can be added/invited via permissions
    so that it's easily overridable for an instance to change behavior.

    A system process is allowed to do anything.
    """

    def __init__(self, *allowed_member_types):
        """Allowed member types."""
        self.allowed_member_types = allowed_member_types

    def needs(self, **kwargs):
        """Enabling needs."""
        return [system_process]

    def excludes(self, member_types=None, **kwargs):
        """Preventing needs."""
        if member_types:
            for m in member_types:
                if m not in self.allowed_member_types:
                    return [any_user]
        return []
