# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test permissions."""

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
