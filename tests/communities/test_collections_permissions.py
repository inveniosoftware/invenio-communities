# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test collections permissions."""

import uuid

import pytest
from invenio_access.permissions import system_identity

from invenio_communities.communities.records.api import Community
from invenio_communities.permissions import CommunityPermissionPolicy


@pytest.fixture(scope="function")
def community(community_service, owner, minimal_community, location):
    """A fresh community for each test to avoid state pollution."""
    # Create a unique slug for each test
    minimal_community = minimal_community.copy()
    minimal_community["slug"] = f"test-community-{uuid.uuid4().hex[:8]}"
    c = community_service.create(owner.identity, minimal_community)
    Community.index.refresh()
    owner.refresh()
    return c


def test_manage_collections_default_permissions(app, community, owner, member_service):
    """Test that owners and managers can manage collections by default."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    # Owner should be able to manage collections
    assert policy(action="manage_collections", record=community_record).allows(
        owner.identity
    )

    # System process should always be able to manage collections
    assert policy(action="manage_collections", record=community_record).allows(
        system_identity
    )


def test_manage_collections_disabled_community(
    app, db, community, owner, any_user, member_service
):
    """Test that collections management is blocked when disabled."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    # Initially, collections are enabled (default)
    assert community_record.access.collections_enabled is True
    assert policy(action="manage_collections", record=community_record).allows(
        owner.identity
    )

    # Disable collections for this community
    community_record.access.collections_enabled = False
    community_record.commit()
    db.session.commit()
    # Owner should NOT be able to manage collections when disabled
    assert not policy(action="manage_collections", record=community_record).allows(
        owner.identity
    )

    # Regular user should also not be able to manage collections
    assert not policy(action="manage_collections", record=community_record).allows(
        any_user.identity
    )


def test_manage_collections_system_process(app, db, community):
    """Test that system process can manage collections even when disabled."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    # Disable collections for this community
    community_record.access.collections_enabled = False
    community_record.commit()
    db.session.commit()

    # System process should still be able to manage collections
    assert policy(action="manage_collections", record=community_record).allows(
        system_identity
    )


def test_manage_collections_insufficient_permissions(
    app, community, any_user, member_service
):
    """Test that users without proper permissions cannot manage collections."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    # Regular user (not a member) should not be able to manage collections
    assert not policy(action="manage_collections", record=community_record).allows(
        any_user.identity
    )


def test_update_collections_enabled_setting(
    app, db, community_service, owner, community
):
    """Test that owners can toggle collections_enabled field."""
    community_record = community._record
    # Initially, collections should be enabled
    assert community_record.access.collections_enabled is True

    # Read the current community data to get all required fields
    current_data = community_service.read(owner.identity, community_record.id).to_dict()

    # Update to disable collections
    current_data["access"]["collections_enabled"] = False
    updated = community_service.update(
        owner.identity,
        community_record.id,
        current_data,
    )

    # Verify the update
    assert updated._record.access.collections_enabled is False
    db.session.commit()

    # Update to re-enable collections
    current_data["access"]["collections_enabled"] = True
    updated2 = community_service.update(
        owner.identity,
        community_record.id,
        current_data,
    )

    # Verify the update
    assert updated2._record.access.collections_enabled is True


def test_collections_enabled_defaults_to_true(
    app, db, community_service, owner, minimal_community
):
    """Test that new communities have collections enabled by default."""
    # Create a unique slug to avoid conflicts
    minimal_community["slug"] = f"test-community-{uuid.uuid4().hex[:8]}"

    # Create a new community without specifying collections_enabled
    new_community = community_service.create(owner.identity, minimal_community)

    # Verify collections are enabled by default
    assert new_community._record.access.collections_enabled is True


def test_manage_collections_with_manager_role(
    app, db, community, owner, new_user, member_service
):
    """Test that community managers cannot manage collections."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    # Add new_user as a manager using system_identity for test setup
    member_data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "manager",
    }
    member_service.add(system_identity, community_record.id, member_data)
    db.session.commit()

    # Manager should not be able to manage collections
    new_user.refresh()
    assert not policy(action="manage_collections", record=community_record).allows(
        new_user.identity
    )


def test_manage_collections_permission_separate_from_update(app, community, owner):
    """Test that manage_collections is a separate permission from update."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    # Both permissions should exist
    can_update = policy(action="update", record=community_record).allows(owner.identity)
    can_manage_collections = policy(
        action="manage_collections", record=community_record
    ).allows(owner.identity)

    # Both should be true for owner, but they are separate permissions
    assert can_update
    assert can_manage_collections

    # Verify the permission policy has both defined
    assert hasattr(policy, "can_update")
    assert hasattr(policy, "can_manage_collections")


def test_collections_enabled_in_access_dump(app, community):
    """Test that collections_enabled is included in access dump."""
    community_record = community._record
    access_dict = community_record.access.dump()

    # Verify collections_enabled is in the dump
    assert "collections_enabled" in access_dict
    assert access_dict["collections_enabled"] is True

    # Change the value and verify it's reflected in dump
    community_record.access.collections_enabled = False
    access_dict = community_record.access.dump()
    assert access_dict["collections_enabled"] is False


def test_collections_enabled_from_dict(app, db):
    """Test that collections_enabled can be loaded from dict."""
    from invenio_communities.communities.records.systemfields.access import (
        CommunityAccess,
    )

    # Create access from dict with collections_enabled=False
    access_dict = {
        "visibility": "public",
        "member_policy": "open",
        "collections_enabled": False,
    }
    access = CommunityAccess.from_dict(access_dict)

    assert access.collections_enabled is False

    # Create access from dict without collections_enabled (should default to True)
    access_dict2 = {
        "visibility": "public",
        "member_policy": "open",
    }
    access2 = CommunityAccess.from_dict(access_dict2)

    assert access2.collections_enabled is True
