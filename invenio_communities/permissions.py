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

import operator
from functools import reduce
from itertools import chain

from elasticsearch_dsl.query import Q
from flask_principal import RoleNeed, UserNeed
from invenio_access.permissions import system_identity
from invenio_cache import current_cache
from invenio_records_permissions.generators import AnyUser, \
    AuthenticatedUser, Generator, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy
from invenio_records_resources.services.errors import PermissionDeniedError

from .communities.records.api import Community


# TODO: Move class to Invenio-Records-Permissions and make more reusable ()
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


class CommunityRoleManager:
    """Manages representations of community role permissions."""

    def __init__(self, community_uuid, role):
        """Constructor."""
        self.community_uuid = community_uuid
        self.role = role

    @classmethod
    def check_string(cls, string):
        """Check if string is a CommunityRole string."""
        return (
            string.startswith("community::") and
            string.count("::") == 2
        )

    @classmethod
    def check_need(cls, need):
        """Check if need is a CommunityRole."""
        return (
            need.method == "role" and
            cls.check_string(need.value)
        )

    @classmethod
    def from_string(cls, string):
        """Constructor from string."""
        assert cls.check_string(string)
        _, c_uuid, role = string.split("::", 3)
        return CommunityRoleManager(c_uuid, role)

    @classmethod
    def from_need(cls, need):
        """Constructor from need."""
        assert cls.check_need(need)
        return cls.from_string(need.value)

    def to_string(self):
        """Create string."""
        return f'community::{self.community_uuid}::{self.role}'

    def to_need(self):
        """Create need."""
        return RoleNeed(self.to_string())


def create_community_role_need(community_id, role):
    """Generate a community role need."""
    return CommunityRoleManager(community_id, role).to_need()


# Community Generators

class CommunityOwner(Generator):
    """Allows community owners."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        community = record

        # Symptom of how api.py objects are falsey if dict empty
        if community is None:
            return []

        return [create_community_role_need(community.id, "owner")]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        users = [n.value for n in identity.provides if n.method == "id"]
        return Q(
            "terms",
            **{"access.owned_by.user": users}
        )


class CommunityManager(Generator):
    """Allows community managers."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        community = record

        # Symptom of how api.py objects are falsey if dict empty
        if community is None:
            return []

        return [create_community_role_need(community.id, "manager")]

    # TODO
    # def query_filter(self, identity=None, **kwargs):
    #     """Filters for current identity."""
    #     pass


class CommunityMember(Generator):
    """Allows a community member."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs.

        :param record: a community
        """
        community = record

        # Symptom of how api.py objects are falsey if dict empty
        if community is None:
            return []

        return [create_community_role_need(community.id, "member")]

    # TODO
    # def query_filter(self, identity=None, **kwargs):
    #     """Filters for current identity."""
    #     pass

# Memberships Generators

class SelfMember(Generator):
    """Allows self (as a member)."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs.

        :param record: a member
        """
        member = record

        # Symptom of how api.py objects are falsey if dict empty
        if member is None:
            return []

        return [UserNeed(member.user_id)]

    # TODO
    # def query_filter(self, identity=None, **kwargs):
    #     """Filters for current identity."""
    #     pass


class OwnerMember(Generator):
    """Allows member that is owner."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs.

        :param record: a member
        """
        member = record

        # Symptom of how api.py objects are falsey if dict empty
        if member is None:
            return []

        return [create_community_role_need(member.community_id, "owner")]


class ManagerMember(Generator):
    """Allows member that is manager."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs.

        :param record: a member
        """
        member = record

        # Symptom of how api.py objects are falsey if dict empty
        if member is None:
            return []

        if member.role == "owner":
            return [create_community_role_need(member.community_id, "owner")]

        return [create_community_role_need(member.community_id, "manager")]

    # TODO
    # def query_filter(self, identity=None, **kwargs):
    #     """Filters for current identity."""
    #     pass

class AnyMember(Generator):
    """Allows any member."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs.

        :param record: a member
        """
        member = record

        # Symptom of how api.py objects are falsey if dict empty
        if member is None:
            return []

        return [create_community_role_need(member.community_id, "member")]


class IfCommunityRestricted(IfRestrictedBase):
    """If Community is restricted."""

    @classmethod
    def get_visiblity(cls, record):
        """Return visibility.

        We have to make a DB call here to fetch the related community.

        :param record: a member
        """
        member = record
        community = Community.get_record(member.community_id)
        return getattr(community.access, "visibility", None)

    def __init__(self, then_, else_):
        """Initialize."""
        super().__init__(
            IfCommunityRestricted.get_visiblity,
            None,
            "restricted",
            "public",
            then_,
            else_,
        )

    def query_filter(self, **kwargs):
        """Don't use this for queries.

        See can_read_search_members.
        """
        raise NotImplementedError()


# Permission Policy

class CommunityPermissionPolicy(BasePermissionPolicy):
    """Permissions for Community CRUD operations."""

    # Community
    can_create = [AuthenticatedUser(), SystemProcess()]

    can_read = [
        IfRestricted(
            'visibility',
            then_=[CommunityOwner()],
            else_=[AnyUser()]),
        ]

    can_update = [CommunityOwner(), SystemProcess()]

    can_delete = [CommunityOwner(), SystemProcess()]

    can_search = [AnyUser(), SystemProcess()]

    can_search_user_communities = [AuthenticatedUser(), SystemProcess()]

    can_rename = [CommunityOwner(), SystemProcess()]

    can_submit_record = [
        IfPolicyClosed(
            'record_policy',
            then_=[CommunityOwner(), SystemProcess()],
            else_=[IfRestricted(
                'visibility',
                then_=[CommunityOwner()],
                else_=[AuthenticatedUser()]),
            ],
        ),
    ]

    # Placed here because passed record is a community
    can_create_member = [CommunityOwner(), CommunityManager(), SystemProcess()]

    can_search_members = [
        SystemProcess(),
        IfRestricted(
            'visibility',
            then_=[CommunityMember()],
            else_=[AnyUser()]
        ),
    ]

    # Members (passed record is a member)

    # This is a new performance enhancing permission to be used when reading
    # a record from the search results.
    # Because can_search_members has already been applied, any user who got
    # through can read the record.
    can_read_search_members = [AnyUser(), SystemProcess()]
    can_read_member = [
        IfCommunityRestricted(
            then_=[AnyMember()],
            else_=[AnyUser()]
        ),
    ]
    can_update_member = [SelfMember(), OwnerMember(), ManagerMember()]
    can_delete_member = [SelfMember(), OwnerMember(), ManagerMember()]


def search_memberships(service, identity):
    """Search for communities identity is part of.

    Just user for now.

    We cannot use high-level service functions here because the given
    identity may not be fully initialized yet, and thus fail permission
    checks.
    """
    return service._search(
        'search_members',
        system_identity,
        params={},
        es_preference=None,
        extra_filter=Q("term", **{"user_id": identity.id}),
        permission_action='read_search_members',
    ).execute()


def load_community_needs(identity, service):
    """Add community-related needs to the freshly loaded identity.

    Note that this function is intended to be called as handler for the
    identity-loaded signal, where we don't have control over the handler
    execution order.
    Thus, the given identity may not be fully initialized and still missing
    some needs (e.g. 'authenticated_user'), so we cannot rely on high-level
    service functions because permission checks may fail.
    """
    if identity.id is None:
        # no user is logged in
        return

    # Cache keys
    #
    # The cache of communities must be invalidated on:
    # 1) on creation of a community (likely this one is modelled via membership
    #    in the future).
    # 2) add/remove/change of membership
    #
    # We construct the cache key for each membership entity (e.g. user,
    # role, system role). This way, once a membership is added/removed/updated
    # we can cache the list of associated communities for this entity.
    # Once a user logs in, we get the cache for each of the membership
    # entities and combine it into a single list.

    # Currently, only users are supported (no roles or system roles)
    cache_key = identity_cache_key(identity)
    memberships = current_cache.get(cache_key)
    if memberships is None:
        try:
            memberships = [
                CommunityRoleManager(m.community_id, m.role).to_string()
                for m in search_memberships(service, identity)
            ]
            current_cache.set(cache_key, memberships, timeout=24*3600)
        except PermissionDeniedError:
            memberships = []

    # Add community needs to identity
    identity.provides.update({
        CommunityRoleManager.from_string(m).to_need() for m in memberships
    })


def on_membership_change(identity=None):
    """Handler called when a membership is changed."""
    if identity is not None:
        current_cache.delete(identity_cache_key(identity))


def identity_cache_key(identity):
    """Make the cache key for storing the communities for a user."""
    return f"user-memberships:{identity.id}"
