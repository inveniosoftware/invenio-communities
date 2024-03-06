# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community members resources."""

import pytest
from invenio_access.permissions import system_identity
from invenio_requests.records.api import RequestEvent


#
# Fixtures
#
@pytest.fixture()
def community_id(community):
    return community._record.id


@pytest.fixture(scope="function")
def group_data(group):
    return {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
    }


@pytest.fixture(scope="function")
def new_user_data(new_user):
    return {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
        "message": "Welcome to the club!",
    }


#
# Add
#
def test_add(client, headers, community_id, owner, group_data, db):
    """Test add REST API."""
    client = owner.login(client)
    r = client.post(
        f"/communities/{community_id}/members", headers=headers, json=group_data
    )
    assert r.status_code == 204


def test_add_denied(client, headers, community_id, group_data, new_user):
    """Test add REST API."""
    client = new_user.login(client)
    r = client.post(
        f"/communities/{community_id}/members", headers=headers, json=group_data
    )
    assert r.status_code == 403


def test_add_bad_data(client, headers, community_id, owner):
    """Test add REST API."""
    client = owner.login(client)
    r = client.post(
        f"/communities/{community_id}/members", headers=headers, json={"members": []}
    )
    assert r.status_code == 400


def test_add_invalid_member(client, headers, community_id, owner, group_data):
    """Test add REST API."""
    client = owner.login(client)
    group_data["members"][0]["id"] = "invalid"
    r = client.post(
        f"/communities/{community_id}/members", headers=headers, json=group_data
    )
    assert r.status_code == 400


def test_add_duplicate(client, headers, community_id, owner, group_data, db):
    """Test add REST API."""
    client = owner.login(client)
    r = client.post(
        f"/communities/{community_id}/members", headers=headers, json=group_data
    )
    assert r.status_code == 204
    r = client.post(
        f"/communities/{community_id}/members", headers=headers, json=group_data
    )
    assert r.status_code == 400


#
# Invite
#
def test_invite(client, headers, community_id, owner, new_user_data, db):
    """Test invite REST API."""
    client = owner.login(client)
    r = client.post(
        f"/communities/{community_id}/invitations",
        headers=headers,
        json=new_user_data,
    )
    assert r.status_code == 204

    RequestEvent.index.refresh()
    r = client.get(f"/communities/{community_id}/invitations", headers=headers)
    assert r.status_code == 200
    request_id = r.json["hits"]["hits"][0]["request"]["id"]

    # check the request
    r = client.get(f"/requests/{request_id}", headers=headers)
    assert r.status_code == 200
    request = r.json
    assert 'You will join as "Reader"' in request["description"]

    # check the timeline
    r = client.get(f"/requests/{request_id}/timeline", headers=headers)
    assert r.status_code == 200
    assert r.json["hits"]["total"] == 1  # invite message
    assert r.json["hits"]["hits"][0]["payload"]["content"] == new_user_data["message"]


def test_invite_deny(client, headers, community_id, new_user, new_user_data, db):
    """Test invite REST API."""
    client = new_user.login(client)
    r = client.post(
        f"/communities/{community_id}/invitations", headers=headers, json=new_user_data
    )
    assert r.status_code == 403


#
# Update
#
def test_update(client, headers, community_id, owner, public_reader):
    """Test update of members."""
    client = owner.login(client)
    data = {
        "members": [{"type": "user", "id": str(public_reader.id)}],
        "visible": False,
        "role": "curator",
    }
    r = client.put(
        f"/communities/{community_id}/members",
        headers=headers,
        json=data,
    )
    assert r.status_code == 204


def test_update_invite(client, headers, community_id, owner, new_user_data, db):
    """Test update of members."""
    client = owner.login(client)
    new_user_data.pop("message")  # not accepted by update
    r = client.post(
        f"/communities/{community_id}/invitations",
        headers=headers,
        json=new_user_data,
    )
    assert r.status_code == 204

    # Update the invite
    new_user_data["role"] = "curator"
    r = client.put(
        f"/communities/{community_id}/invitations",
        headers=headers,
        json=new_user_data,
    )
    assert r.status_code == 204


#
# Delete
#
def test_delete(client, headers, community_id, owner, public_reader):
    """Test delete of members."""
    client = public_reader.login(client)
    data = {
        "members": [{"type": "user", "id": str(public_reader.id)}],
    }
    r = client.delete(
        f"/communities/{community_id}/members",
        headers=headers,
        json=data,
    )
    assert r.status_code == 204


@pytest.fixture(scope="function")
def extra_user(app, db, UserFixture, member_service, community):
    """Add a reader member with public visibility."""
    u = UserFixture(
        email="extra@newuser.org",
        password="newuser",
        user_profile={
            "full_name": "Should be last",
        },
        preferences={
            "visibility": "public",
            "email_visibility": "restricted",
        },
        active=True,
        confirmed=True,
    )
    u.create(app, db)
    data = {
        "members": [{"type": "user", "id": str(u.id)}],
        "role": "reader",
        "visible": True,
    }

    member_service.add(system_identity, community._record.id, data)
    return u


#
# Search and serialization
#
def test_search(
    db,
    clean_index,
    client,
    headers,
    extra_user,
    community_id,
    owner,
    public_reader,
):
    """Search."""
    client = owner.login(client)
    r = client.get(
        f"/communities/{community_id}/members",
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json
    assert data["sortBy"] == "name"
    assert data["hits"]["total"] == 3
    assert "role" in data["aggregations"]
    assert "visibility" in data["aggregations"]

    hit = data["hits"]["hits"][0]
    assert "role" in hit
    assert "visible" in hit
    assert "created" in hit
    assert "updated" in hit
    assert "revision_id" in hit
    assert "is_current_user" in hit
    assert "permissions" in hit
    assert hit["permissions"]["can_leave"] is False
    assert hit["permissions"]["can_delete"] is True
    assert hit["permissions"]["can_update_role"] is True
    assert hit["permissions"]["can_update_visible"] is True
    assert hit["visible"] is True

    hit = data["hits"]["hits"][1]  # should be last, test sorting
    assert hit["member"]["name"] == "Should be last"

    # third because of no name
    hit = data["hits"]["hits"][2]
    assert hit["is_current_user"] is True
    assert hit["permissions"]["can_leave"] is True
    assert hit["permissions"]["can_delete"] is False
    assert hit["permissions"]["can_update_role"] is False
    assert hit["permissions"]["can_update_visible"] is True
    assert hit["visible"] is False

    # Pagination params should be passed correctly as well.
    # see https://github.com/inveniosoftware/invenio-communities/issues/495
    r1 = client.get(
        f"/communities/{community_id}/members",
        headers=headers,
        query_string={"page": 1, "size": 1},
    ).json
    assert r1["hits"]["total"] == 3
    assert len(r1["hits"]["hits"]) == 1

    r2 = client.get(
        f"/communities/{community_id}/members",
        headers=headers,
        query_string={"page": 3, "size": 1},
    ).json
    assert r2["hits"]["total"] == 3
    assert len(r2["hits"]["hits"]) == 1
    assert r1["hits"]["hits"][0]["id"] != r2["hits"]["hits"][0]


def test_search_public(
    client, headers, community_id, new_user, public_reader, clean_index
):
    """Search public members."""
    client = new_user.login(client)
    r = client.get(
        f"/communities/{community_id}/members/public",
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json
    assert data["sortBy"] == "name"
    assert data["hits"]["total"] == 1
    hit = data["hits"]["hits"][0]
    # Public view has no facets (because that would leak information on
    # roles/visible)
    assert "aggregations" not in data
    # A member in the public view should not leak below attributes:
    assert "role" not in hit
    assert "visible" not in hit
    assert "created" not in hit
    assert "updated" not in hit
    assert "revision_id" not in hit
    assert "is_current_user" not in hit
    assert "permissions" not in hit
    # A member do have:
    assert "member" in hit
    assert "id" in hit["member"]
    assert "type" in hit["member"]
    assert "name" in hit["member"]
    assert "description" in hit["member"]


def test_search_invitation(
    client, headers, community_id, owner, invite_user, db, clean_index
):
    """Search invitations."""
    client = owner.login(client)
    r = client.get(
        f"/communities/{community_id}/invitations",
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json
    assert data["hits"]["total"] == 1
    assert "role" in data["aggregations"]
    assert "status" in data["aggregations"]
    hit = data["hits"]["hits"][0]
    assert "role" in hit
    assert "visible" in hit
    assert "created" in hit
    assert "updated" in hit
    assert "revision_id" in hit
    assert "request" in hit
    assert "id" in hit["request"]
    assert "status" in hit["request"]
    assert "expires_at" in hit["request"]
    assert hit["request"]["expires_at"] is not None
    assert "permissions" in hit
    assert hit["permissions"]["can_update_role"] is True
    assert hit["permissions"]["can_cancel"] is True


# TODO: member serialization/links
# TODO: request serialization/links
# TODO: community member can see info
# TODO: community non-member can't see info
# TODO: facet by role, facet by visibility, define sorts.
# TODO: same user can be invited to two different communities
# TODO: same user/group can be added to two different communities
