# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test permissions.

Really this is only testing member-related permissions currently, but since
CommunityPermissionPolicy is defined at the top-level, the test are defined there too.
"""

import copy

from flask_principal import Identity

from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.permissions import CommunityPermissionPolicy


def test_can_request_membership(
    app,
    community,
    community_open_to_membership_requests,
    owner,
    anon_identity,
    any_user,
    superuser_identity,
    set_app_config_fn_scoped,
):
    policy = CommunityPermissionPolicy
    community_closed_record = community._record
    community_open_record = community_open_to_membership_requests._record
    identity_authenticated = any_user.identity
    identity_superuser = superuser_identity  # just to parallel naming
    identity_anonymous = anon_identity  # just to parallel naming
    set_app_config_fn_scoped({"COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS": False})
    # subsequent config changes can be done directly, knowing they will all be
    # roll-backed correctly

    # Case: config disabled - nobody can request membership
    assert not (
        policy(action="request_membership", record=community_open_record).allows(
            identity_authenticated
        )
    )
    assert not (
        policy(action="request_membership", record=community_open_record).allows(
            identity_superuser
        )
    )

    # Case: config enabled but setting disabled - nobody can request membership
    app.config["COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS"] = True
    assert not (
        policy(action="request_membership", record=community_closed_record).allows(
            identity_authenticated
        )
    )
    assert not (
        policy(action="request_membership", record=community_closed_record).allows(
            identity_superuser
        )
    )

    # Case - config enabled, setting enabled - unlogged user can't request
    assert not (
        policy(action="request_membership", record=community_open_record).allows(
            identity_anonymous
        )
    )
    # Case - config enabled, setting enabled - already member of community can't request
    assert not (
        policy(action="request_membership", record=community_open_record).allows(
            owner.identity
        )
    )
    # Case - config enabled, setting enabled - authenticated but not member of community
    assert policy(action="request_membership", record=community_open_record).allows(
        identity_authenticated
    )


def test_can_search_request_membership(
    app,
    community,
    community_open_to_membership_requests,
    create_user,
    owner,
    anon_identity,
    any_user,
    superuser_identity,
    set_app_config_fn_scoped,
):
    policy = CommunityPermissionPolicy
    action = "search_membership_requests"
    community_open_record = community_open_to_membership_requests._record
    community_closed_record = community._record
    identity_anonymous = anon_identity  # just to parallel naming
    identity_authenticated = any_user.identity
    identity_superuser = superuser_identity  # just to parallel naming
    set_app_config_fn_scoped({"COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS": False})

    # Case: config disabled - nobody can search request memberships
    assert not (
        policy(action=action, record=community_open_record).allows(
            identity_authenticated
        )
    )
    assert not (
        policy(action=action, record=community_open_record).allows(identity_superuser)
    )

    # Case: config enabled but setting disabled - nobody can search request memberships
    app.config["COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS"] = True
    assert not (
        policy(action=action, record=community_closed_record).allows(
            identity_authenticated
        )
    )
    assert not (
        policy(action=action, record=community_closed_record).allows(identity_superuser)
    )

    # Case - config enabled, setting enabled
    # anonymous
    assert not (
        policy(action=action, record=community_open_record).allows(identity_anonymous)
    )
    # owner
    assert policy(action=action, record=community_open_record).allows(owner.identity)
    # other roles
    user = create_user()
    identity_orig = Identity(user.id)
    identity = copy.deepcopy(identity_orig)
    needs = {
        role: CommunityRoleNeed(value=str(community_open_record.id), role=role)
        for role in ["manager", "curator", "reader"]
    }
    identity.provides = identity_orig.provides.union({needs["manager"]})
    assert policy(action=action, record=community_open_record).allows(identity)
    identity.provides = identity_orig.provides.union({needs["curator"]})
    assert not policy(action=action, record=community_open_record).allows(identity)
    identity.provides = identity_orig.provides.union({needs["reader"]})
    assert not policy(action=action, record=community_open_record).allows(identity)
