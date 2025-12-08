# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test group notification preferences REST API."""

import pytest
from invenio_access.permissions import system_identity


#
# Fixtures
#
@pytest.fixture()
def community_id(community):
    return community._record.id


@pytest.fixture(scope="function")
def group_data_with_notification(group):
    return {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": False,
    }


@pytest.fixture(scope="function")
def group_data(group):
    return {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
    }


#
# Add groups with notification preference
#
def test_add_group_with_notification_enabled(
    client, headers, community_id, owner, group, db, member_service, clean_index
):
    """Test adding a group with notification explicitly enabled via REST API."""
    client = owner.login(client)
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": True,
    }
    r = client.post(f"/communities/{community_id}/members", headers=headers, json=data)
    assert r.status_code == 204

    # Wait for indexing
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify the notification setting was saved
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200
    group_member = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ][0]
    assert group_member["group_notification_enabled"] is True


def test_add_group_with_notification_disabled(
    client,
    headers,
    community_id,
    owner,
    group_data_with_notification,
    db,
    member_service,
    clean_index,
):
    """Test adding a group with notification disabled via REST API."""
    client = owner.login(client)
    r = client.post(
        f"/communities/{community_id}/members",
        headers=headers,
        json=group_data_with_notification,
    )
    assert r.status_code == 204

    # Wait for indexing
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify the notification setting was saved
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200
    group_member = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ][0]
    assert group_member["group_notification_enabled"] is False


def test_add_group_notification_default(
    client, headers, community_id, owner, group_data, db, member_service, clean_index
):
    """Test that notification defaults to enabled when not specified via REST API."""
    client = owner.login(client)
    r = client.post(
        f"/communities/{community_id}/members", headers=headers, json=group_data
    )
    assert r.status_code == 204

    # Wait for indexing
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify notification is enabled by default
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200
    group_member = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ][0]
    assert group_member["group_notification_enabled"] is True


def test_add_group_notification_invalid_type(
    client, headers, community_id, owner, group, db
):
    """Test that invalid notification type returns 400 via REST API."""
    client = owner.login(client)
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": ["invalid"],  # Should be boolean
    }
    r = client.post(f"/communities/{community_id}/members", headers=headers, json=data)
    assert r.status_code == 400


#
# Update group notification preference
#
def test_update_group_notification(
    client, headers, community_id, owner, group_data, db, member_service, clean_index
):
    """Test updating group notification preference via REST API."""
    # Add a group member first
    member_service.add(owner.identity, community_id, group_data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Update notification preference
    client = owner.login(client)
    update_data = {
        "members": group_data["members"],
        "group_notification_enabled": False,
    }
    r = client.put(
        f"/communities/{community_id}/members", headers=headers, json=update_data
    )
    assert r.status_code == 204

    # Wait for indexing
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify the update
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200
    group_member = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ][0]
    assert group_member["group_notification_enabled"] is False


def test_update_group_notification_with_role(
    client, headers, community_id, owner, group_data, db, member_service, clean_index
):
    """Test updating both notification and role via REST API."""
    # Add a group member first
    member_service.add(owner.identity, community_id, group_data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Update both notification and role
    client = owner.login(client)
    update_data = {
        "members": group_data["members"],
        "role": "curator",
        "group_notification_enabled": False,
    }
    r = client.put(
        f"/communities/{community_id}/members", headers=headers, json=update_data
    )
    assert r.status_code == 204

    # Wait for indexing
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify both updates
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200
    group_member = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ][0]
    assert group_member["group_notification_enabled"] is False
    assert group_member["role"] == "curator"


def test_update_group_notification_denied(
    client, headers, community_id, members, group_data, db, member_service
):
    """Test that non-privileged users cannot update notification via REST API."""
    # Add a group member first
    member_service.add(system_identity, community_id, group_data)

    # Try to update as a reader (should fail)
    client = members["reader"].login(client)
    update_data = {
        "members": group_data["members"],
        "group_notification_enabled": False,
    }
    r = client.put(
        f"/communities/{community_id}/members", headers=headers, json=update_data
    )
    assert r.status_code == 403


def test_update_group_notification_invalid_type(
    client, headers, community_id, owner, group_data, db, member_service
):
    """Test that invalid notification type returns 400 on update via REST API."""
    # Add a group member first
    member_service.add(owner.identity, community_id, group_data)

    # Try to update with invalid type (list can't be converted to boolean)
    client = owner.login(client)
    update_data = {
        "members": group_data["members"],
        "group_notification_enabled": ["invalid"],  # Should be boolean
    }
    r = client.put(
        f"/communities/{community_id}/members", headers=headers, json=update_data
    )
    assert r.status_code == 400


#
# Search and verify notification field
#
def test_search_includes_notification_field(
    client, headers, community_id, owner, group_data, db, member_service, clean_index
):
    """Test that search results include notification field via REST API."""
    # Add a group member with notification disabled
    group_data["group_notification_enabled"] = False
    member_service.add(owner.identity, community_id, group_data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Search and verify field is present
    client = owner.login(client)
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200

    group_member = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ][0]

    assert "group_notification_enabled" in group_member
    assert group_member["group_notification_enabled"] is False


def test_search_includes_notification_permission(
    client, headers, community_id, owner, group_data, db, member_service, clean_index
):
    """Test that search results include can_update_group_notification permission."""
    # Add a group member
    member_service.add(owner.identity, community_id, group_data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Search and verify permission is present
    client = owner.login(client)
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200

    group_member = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ][0]

    assert "permissions" in group_member
    assert "can_update_group_notification" in group_member["permissions"]
    assert group_member["permissions"]["can_update_group_notification"] is True


def test_user_member_no_notification_field(
    client, headers, community_id, owner, new_user, db, member_service, clean_index
):
    """Test that user members don't have notification field via REST API."""
    # Add a user member
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.add(system_identity, community_id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Search and verify field is not set for users
    client = owner.login(client)
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200

    user_member = [m for m in r.json["hits"]["hits"] if m["member"]["type"] == "user"][
        0
    ]

    # User should not have this field set (or it should be None)
    assert user_member.get("group_notification_enabled") is None
    # But permission should be False for users
    assert user_member["permissions"]["can_update_group_notification"] is False


#
# Edge cases
#
def test_update_only_notification_field(
    client, headers, community_id, owner, group_data, db, member_service, clean_index
):
    """Test updating only notification field without role or visibility."""
    # Add a group member
    member_service.add(owner.identity, community_id, group_data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Update only notification
    client = owner.login(client)
    update_data = {
        "members": group_data["members"],
        "group_notification_enabled": False,
    }
    r = client.put(
        f"/communities/{community_id}/members", headers=headers, json=update_data
    )
    assert r.status_code == 204

    # Wait for indexing
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify only notification changed
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200
    group_member = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ][0]
    assert group_member["group_notification_enabled"] is False
    assert group_member["role"] == "reader"  # Original role unchanged


def test_update_multiple_groups_different_notifications(
    client, headers, community_id, owner, database, db, member_service, clean_index
):
    """Test updating multiple groups with different notification preferences."""
    from invenio_accounts.models import Role

    # Create two groups
    group1 = Role(id="notif-group-1", name="notif-group-1")
    group2 = Role(id="notif-group-2", name="notif-group-2")
    database.session.add(group1)
    database.session.add(group2)
    database.session.commit()

    # Add both groups
    data1 = {
        "members": [{"type": "group", "id": group1.name}],
        "role": "reader",
    }
    data2 = {
        "members": [{"type": "group", "id": group2.name}],
        "role": "reader",
    }
    member_service.add(owner.identity, community_id, data1)
    member_service.add(owner.identity, community_id, data2)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Update first group to disabled
    client = owner.login(client)
    update_data = {
        "members": [{"type": "group", "id": group1.name}],
        "group_notification_enabled": False,
    }
    r = client.put(
        f"/communities/{community_id}/members", headers=headers, json=update_data
    )
    assert r.status_code == 204

    # Wait for indexing
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify only first group was updated
    r = client.get(f"/communities/{community_id}/members", headers=headers)
    assert r.status_code == 200

    group_members = [
        m for m in r.json["hits"]["hits"] if m["member"]["type"] == "group"
    ]

    group1_member = [m for m in group_members if m["member"]["id"] == group1.name][0]
    group2_member = [m for m in group_members if m["member"]["id"] == group2.name][0]

    assert group1_member["group_notification_enabled"] is False
    assert (
        group2_member["group_notification_enabled"] is True
    )  # Should still be default
