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
    minimal_community = minimal_community.copy()
    minimal_community["slug"] = f"test-community-{uuid.uuid4().hex[:8]}"
    c = community_service.create(owner.identity, minimal_community)
    Community.index.refresh()
    owner.refresh()
    return c


def test_manage_collections_default_permissions(app, community, owner, member_service):
    """Test that owners and system process can manage collections by default."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    assert policy(action="manage_collections", record=community_record).allows(
        owner.identity
    )
    assert policy(action="manage_collections", record=community_record).allows(
        system_identity
    )


def test_manage_collections_insufficient_permissions(
    app, community, any_user, member_service
):
    """Test that users without proper permissions cannot manage collections."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    assert not policy(action="manage_collections", record=community_record).allows(
        any_user.identity
    )


def test_manage_collections_with_manager_role(
    app, db, community, owner, new_user, member_service
):
    """Test that community managers cannot manage collections."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    member_data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "manager",
    }
    member_service.add(system_identity, community_record.id, member_data)
    db.session.commit()

    new_user.refresh()
    assert not policy(action="manage_collections", record=community_record).allows(
        new_user.identity
    )


def test_manage_collections_permission_separate_from_update(app, community, owner):
    """Test that manage_collections is a separate permission from update."""
    policy = CommunityPermissionPolicy
    community_record = community._record

    can_update = policy(action="update", record=community_record).allows(owner.identity)
    can_manage_collections = policy(
        action="manage_collections", record=community_record
    ).allows(owner.identity)

    assert can_update
    assert can_manage_collections
    assert hasattr(policy, "can_update")
    assert hasattr(policy, "can_manage_collections")
