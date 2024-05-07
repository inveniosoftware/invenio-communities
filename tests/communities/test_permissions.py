# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test permissions."""

from invenio_communities.permissions import CommunityPermissionPolicy


def test_can_request_membership(
    app, community, owner, anon_identity, any_user, superuser_identity
):

    policy = CommunityPermissionPolicy
    community_record = community._record
    authenticated_identity = any_user.identity

    allow_membership_requests_orig = app.config["COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS"]

    # Case - feature disabled
    app.config["COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS"] = False
    assert not (
        policy(action="request_membership", record=community_record).allows(
            superuser_identity
        )
    )

    app.config["COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS"] = True

    # Case - setting disabled
    community_record.access.member_policy = "closed"
    assert not (
        policy(action="request_membership", record=community_record).allows(
            superuser_identity
        )
    )

    community_record.access.member_policy = "open"

    # Case - unlogged user
    assert not (
        policy(action="request_membership", record=community_record).allows(
            anon_identity
        )
    )

    # Case - logged user not part of community
    assert policy(action="request_membership", record=community_record).allows(
        authenticated_identity
    )

    # Case - member of community
    assert not (
        policy(action="request_membership", record=community_record).allows(
            owner.identity
        )
    )

    app.config["COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS"] = allow_membership_requests_orig
