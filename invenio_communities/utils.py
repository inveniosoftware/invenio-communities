# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities."""

from elasticsearch_dsl import Q
from invenio_cache import current_cache
from invenio_records_resources.services.errors import PermissionDeniedError

from .generators import CommunityRoleNeed


def search_communities(service, identity):
    """Search for communities owned by the given identity.

    We cannot use high-level service functions here because the given
    identity may not be fully initialized yet, and thus fail permission
    checks.
    """
    # TODO this needs to be revisited once memberships are in!
    search_result = service._search(
        'search',
        identity,
        params={},
        es_preference=None,
        extra_filter=Q(
            "term",
            **{"access.owned_by.user": identity.id}
        ),
        permission_action='read',
    ).execute()

    return search_result


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
    communities = current_cache.get(cache_key)
    if communities is None:
        try:
            communities = []
            for c in search_communities(service, identity):
                communities.append(str(c.uuid))
            current_cache.set(cache_key, communities, timeout=24*3600)
        except PermissionDeniedError:
            communities = []


    # Add community needs to identity
    for c_id in communities:
        identity.provides.add(CommunityRoleNeed(c_id, 'owner'))


def on_membership_change(identity=None):
    """Handler called when a membership is changed."""
    if identity is not None:
        current_cache.delete(identity_cache_key(identity))

def identity_cache_key(identity):
    """Make the cache key for storing the communities for a user."""
    return f"user-communities:{identity.id}"
