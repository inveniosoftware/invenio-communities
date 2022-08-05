# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities."""

from invenio_cache import current_cache

from .generators import CommunityRoleNeed
from .proxies import current_communities


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
    community_roles = current_cache.get(cache_key)
    if community_roles is None:
        # aka Member.get_memberships(identity)
        community_roles = (
            current_communities.service.members.config.record_cls.get_memberships(
                identity
            )
        )
        current_cache.set(cache_key, community_roles, timeout=24 * 3600)

    # Add community needs to identity
    for c_id, role in community_roles:
        identity.provides.add(CommunityRoleNeed(c_id, role))


def on_membership_change(identity=None):
    """Handler called when a membership is changed."""
    if identity is not None:
        current_cache.delete(identity_cache_key(identity))


def identity_cache_key(identity):
    """Make the cache key for storing the communities for a user."""
    return f"user-communities:{identity.id}"
