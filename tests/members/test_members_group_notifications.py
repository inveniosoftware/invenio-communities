# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test group notification preferences for community members."""

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError


#
# Add groups with notification preference
#
def test_add_group_notification_enabled_default(
    member_service, community, owner, group, db
):
    """Test that group notification is enabled by default."""
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
    }
    member_service.add(owner.identity, community._record.id, data)

    # Search for the member
    res = member_service.search(owner.identity, community._record.id).to_dict()
    group_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"][0]

    # Verify notification is enabled by default
    assert group_member["group_notification_enabled"] is True


def test_add_group_notification_enabled_explicit(
    member_service, community, owner, group, db
):
    """Test adding group with notification explicitly enabled."""
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": True,
    }
    member_service.add(owner.identity, community._record.id, data)

    # Search for the member
    res = member_service.search(owner.identity, community._record.id).to_dict()
    group_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"][0]

    assert group_member["group_notification_enabled"] is True


def test_add_group_notification_disabled(
    member_service, community, owner, group, db, clean_index
):
    """Test adding group with notification explicitly disabled."""
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": False,
    }
    member_service.add(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Search for the member
    res = member_service.search(owner.identity, community._record.id).to_dict()
    group_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"][0]

    assert group_member["group_notification_enabled"] is False


def test_add_user_notification_preference_ignored(
    member_service, community, new_user, db
):
    """Test that notification preference is ignored for user members."""
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
        "group_notification_enabled": False,  # Should be ignored for users
    }
    member_service.add(system_identity, community._record.id, data)

    # Search for the member
    res = member_service.search(system_identity, community._record.id).to_dict()
    user_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "user"][0]

    # User members should not have this field set
    assert user_member.get("group_notification_enabled") is None


#
# Update group notification preference
#
@pytest.mark.parametrize(
    "actor,role",
    [
        ("owner", "reader"),
        ("owner", "manager"),
        ("manager", "reader"),
        ("manager", "curator"),
    ],
)
def test_update_group_notification_allowed(
    member_service, community, members, group, actor, role, db, clean_index
):
    """Test that owners and managers can update group notification preferences."""
    # Add a group member
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": role,
        "group_notification_enabled": True,
    }
    member_service.add(system_identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Update notification preference to disabled
    data = {
        "members": [{"type": "group", "id": group.name}],
        "group_notification_enabled": False,
    }
    member_service.update(members[actor].identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify the update
    res = member_service.search(members[actor].identity, community._record.id).to_dict()
    group_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"][0]
    assert group_member["group_notification_enabled"] is False


@pytest.mark.parametrize(
    "actor",
    ["curator", "reader"],
)
def test_update_group_notification_denied(
    member_service, community, members, group, actor, db
):
    """Test that curators and readers cannot update group notification preferences."""
    # Add a group member
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": True,
    }
    member_service.add(system_identity, community._record.id, data)

    # Try to update notification preference
    data = {
        "members": [{"type": "group", "id": group.name}],
        "group_notification_enabled": False,
    }
    assert pytest.raises(
        PermissionDeniedError,
        member_service.update,
        members[actor].identity,
        community._record.id,
        data,
    )


def test_update_group_notification_toggle(
    member_service, community, owner, group, db, clean_index
):
    """Test toggling notification preference multiple times."""
    # Add a group member with notifications enabled
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": True,
    }
    member_service.add(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Toggle to disabled
    data = {
        "members": [{"type": "group", "id": group.name}],
        "group_notification_enabled": False,
    }
    member_service.update(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    res = member_service.search(owner.identity, community._record.id).to_dict()
    group_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"][0]
    assert group_member["group_notification_enabled"] is False

    # Toggle back to enabled
    data = {
        "members": [{"type": "group", "id": group.name}],
        "group_notification_enabled": True,
    }
    member_service.update(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    res = member_service.search(owner.identity, community._record.id).to_dict()
    group_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"][0]
    assert group_member["group_notification_enabled"] is True


def test_update_group_notification_with_role(
    member_service, community, owner, group, db, clean_index
):
    """Test updating notification preference along with role."""
    # Add a group member
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": True,
    }
    member_service.add(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Update both role and notification preference
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "curator",
        "group_notification_enabled": False,
    }
    member_service.update(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify both updates
    res = member_service.search(owner.identity, community._record.id).to_dict()
    group_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"][0]
    assert group_member["role"] == "curator"
    assert group_member["group_notification_enabled"] is False


def test_update_user_notification_preference_ignored(
    member_service, community, owner, new_user, db
):
    """Test that notification preference updates are ignored for user members."""
    # Add a user member
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.add(system_identity, community._record.id, data)

    # Try to update notification preference (should be ignored)
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "group_notification_enabled": False,
    }
    # This should succeed but the field should remain None for users
    member_service.update(owner.identity, community._record.id, data)

    res = member_service.search(owner.identity, community._record.id).to_dict()
    user_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "user"][0]

    # User members should still not have this field set
    assert user_member.get("group_notification_enabled") is None


#
# Validation tests
#
def test_add_group_notification_invalid_type(
    member_service, community, owner, group, db
):
    """Test that invalid notification preference type raises error."""
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
        "group_notification_enabled": ["invalid"],  # Should be boolean
    }
    with pytest.raises(ValidationError):
        member_service.add(
            owner.identity,
            community._record.id,
            data,
        )


def test_update_group_notification_invalid_type(
    member_service, community, owner, group, db, clean_index
):
    """Test that invalid notification preference type raises error on update."""
    # Add a group member
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
    }
    member_service.add(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Try to update with invalid type (list can't be converted to boolean)
    data = {
        "members": [{"type": "group", "id": group.name}],
        "group_notification_enabled": ["invalid"],  # Should be boolean
    }
    with pytest.raises(ValidationError):
        member_service.update(
            owner.identity,
            community._record.id,
            data,
        )


#
# Permissions tests
#
def test_group_notification_permission_in_response(
    member_service, community, owner, group, db
):
    """Test that can_update_group_notification permission is included in response."""
    # Add a group member
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
    }
    member_service.add(owner.identity, community._record.id, data)

    # Search for the member
    res = member_service.search(owner.identity, community._record.id).to_dict()
    group_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"][0]

    # Verify permission is present and True for owner
    assert "can_update_group_notification" in group_member["permissions"]
    assert group_member["permissions"]["can_update_group_notification"] is True


def test_user_notification_permission_not_in_response(
    member_service, community, new_user, db
):
    """Test that can_update_group_notification is False for user members."""
    # Add a user member
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.add(system_identity, community._record.id, data)

    # Search for the member
    res = member_service.search(system_identity, community._record.id).to_dict()
    user_member = [m for m in res["hits"]["hits"] if m["member"]["type"] == "user"][0]

    # Verify permission is present but False for user members
    assert "can_update_group_notification" in user_member["permissions"]
    assert user_member["permissions"]["can_update_group_notification"] is False


#
# Multiple groups tests
#
def test_add_multiple_groups_with_different_notifications(
    member_service, community, owner, database, clean_index
):
    """Test adding multiple groups with different notification preferences."""
    from invenio_accounts.models import Role

    # Create two groups
    group1 = Role(id="group-1", name="group-1")
    group2 = Role(id="group-2", name="group-2")
    database.session.add(group1)
    database.session.add(group2)
    database.session.commit()

    # Add first group with notifications enabled
    data = {
        "members": [{"type": "group", "id": group1.name}],
        "role": "reader",
        "group_notification_enabled": True,
    }
    member_service.add(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Add second group with notifications disabled
    data = {
        "members": [{"type": "group", "id": group2.name}],
        "role": "reader",
        "group_notification_enabled": False,
    }
    member_service.add(owner.identity, community._record.id, data)
    member_service.indexer.process_bulk_queue()
    member_service.record_cls.index.refresh()

    # Verify both groups have correct settings
    res = member_service.search(owner.identity, community._record.id).to_dict()
    group_members = [m for m in res["hits"]["hits"] if m["member"]["type"] == "group"]

    group1_member = [m for m in group_members if m["member"]["id"] == group1.name][0]
    group2_member = [m for m in group_members if m["member"]["id"] == group2.name][0]

    assert group1_member["group_notification_enabled"] is True
    assert group2_member["group_notification_enabled"] is False
