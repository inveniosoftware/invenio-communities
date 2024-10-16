# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Northwestern University.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test permissions."""
from flask_principal import Identity, RoleNeed
from invenio_access.permissions import system_identity

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


def test_can_create(app, anon_identity, any_user, superuser_identity):
    policy = CommunityPermissionPolicy

    # Save the original configuration value
    original_config = app.config.get("RDM_COMMUNITY_REQUIRED_TO_PUBLISH", False)

    authenticated_identity = any_user.identity

    # Create an identity for a user with the 'community-creator' role
    # Copy the provides from authenticated_identity to ensure 'authenticated_user' is included
    community_creator_identity = Identity(any_user.id)
    community_creator_identity.provides.update(authenticated_identity.provides)
    community_creator_identity.provides.add(RoleNeed("community-creator"))

    # RDM_COMMUNITY_REQUIRED_TO_PUBLISH is True
    app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = True

    # Anonymous user cannot create communities
    assert not policy(action="create").allows(anon_identity)

    # Authenticated user without 'community-creator' role cannot create
    assert not policy(action="create").allows(authenticated_identity)

    # Authenticated user with 'community-creator' role can create
    assert policy(action="create").allows(community_creator_identity)

    # Superuser (admin) can create communities
    assert policy(action="create").allows(superuser_identity)

    # System process can create communities
    assert policy(action="create").allows(system_identity)

    # RDM_COMMUNITY_REQUIRED_TO_PUBLISH is False
    app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = False

    # Anonymous user cannot create communities
    assert not policy(action="create").allows(anon_identity)

    # Authenticated user without 'community-creator' role can create
    assert policy(action="create").allows(authenticated_identity)

    # Authenticated user with 'community-creator' role can create
    assert policy(action="create").allows(community_creator_identity)

    # Superuser (admin) can create communities
    assert policy(action="create").allows(superuser_identity)

    # System process can create communities
    assert policy(action="create").allows(system_identity)
