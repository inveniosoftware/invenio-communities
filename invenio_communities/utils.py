# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities."""

from flask import session
from flask_principal import Identity
from invenio_accounts.models import Role
from invenio_accounts.proxies import current_db_change_history

from .generators import CommunityRoleNeed
from .proxies import current_communities, current_identities_cache

IDENTITY_KEY = "user-communities:"


def load_community_needs(identity):
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
    community_roles = current_identities_cache.get(cache_key)
    if community_roles is None:
        # aka Member.get_memberships(identity)
        roles_ids = session.get("unmanaged_roles_ids", [])

        member_cls = current_communities.service.members.config.record_cls
        managed_community_roles = member_cls.get_memberships(identity)
        unmanaged_community_roles = member_cls.get_memberships_from_group_ids(
            identity, roles_ids
        )
        community_roles = managed_community_roles + unmanaged_community_roles

        for community_id, role in community_roles:
            current_identities_cache.append(community_id, identity.id)
            # Add community needs to identity
            identity.provides.add(CommunityRoleNeed(community_id, role))

        current_identities_cache.set(
            cache_key,
            community_roles,
        )
    else:
        # Add community needs to identity
        for community_id, role in community_roles:
            identity.provides.add(CommunityRoleNeed(community_id, role))


def on_user_membership_change(identity=None):
    """Handler called when a user membership is changed."""
    if identity is not None:
        current_identities_cache.delete(identity_cache_key(identity))


def on_group_membership_change(community_id):
    """Handler called when a group membership is changed."""
    community_identities_cache = current_identities_cache.get(community_id)
    if community_identities_cache:
        for identity in community_identities_cache:
            on_user_membership_change(Identity(identity))


def identity_cache_key(identity):
    """Make the cache key for storing the communities for a user."""
    return f"{IDENTITY_KEY}{identity.id}"


def on_datastore_post_commit(sender, session):
    """Clears the cache for the user identity."""
    sid = id(session)
    if current_db_change_history.sessions.get(sid):
        for user_id in current_db_change_history.sessions[sid].updated_users:
            on_user_membership_change(Identity(user_id))

        for user_id in current_db_change_history.sessions[sid].deleted_users:
            on_user_membership_change(Identity(user_id))

        for role_id in current_db_change_history.sessions[sid].deleted_roles:
            role = Role.query.filter_by(id=role_id).one_or_none()
            users = role.users.all()
            for user in users:
                on_user_membership_change(Identity(user.id))
