# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community members resources."""

import pytest


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
    }

#
# Add
#
def test_add(client, headers, community_id, owner, group_data, db):
    """Test add REST API."""
    client = owner.login(client)
    r = client.post(
        f'/communities/{community_id}/members',
        headers=headers,
        json=group_data
    )
    assert r.status_code == 204


def test_add_denied(client, headers, community_id, group_data, new_user):
    """Test add REST API."""
    client = new_user.login(client)
    r = client.post(
        f'/communities/{community_id}/members',
        headers=headers,
        json=group_data
    )
    assert r.status_code == 403


def test_add_bad_data(client, headers, community_id, owner):
    """Test add REST API."""
    client = owner.login(client)
    r = client.post(
        f'/communities/{community_id}/members',
        headers=headers,
        json={"members": []}
    )
    assert r.status_code == 400


def test_add_invalid_member(client, headers, community_id, owner, group_data):
    """Test add REST API."""
    client = owner.login(client)
    group_data['members'][0]['id'] = 'invalid'
    r = client.post(
        f'/communities/{community_id}/members',
        headers=headers,
        json=group_data
    )
    assert r.status_code == 400


def test_add_duplicate(client, headers, community_id, owner, group_data, db):
    """Test add REST API."""
    client = owner.login(client)
    r = client.post(
        f'/communities/{community_id}/members',
        headers=headers,
        json=group_data
    )
    assert r.status_code == 204
    r = client.post(
        f'/communities/{community_id}/members',
        headers=headers,
        json=group_data
    )
    assert r.status_code == 400


#
# Invite
#
def test_invite(client, headers, community_id, owner, new_user_data, db):
    """Test invite REST API."""
    client = owner.login(client)
    r = client.post(
        f'/communities/{community_id}/invitations',
        headers=headers,
        json=new_user_data,
    )
    assert r.status_code == 204


def test_invite_deny(
        client, headers, community_id, new_user, new_user_data, db):
    """Test invite REST API."""
    client = new_user.login(client)
    r = client.post(
        f'/communities/{community_id}/invitations',
        headers=headers,
        json=new_user_data
    )
    assert r.status_code == 403


#
# Update
#
def test_update(
        client, headers, community_id, owner, public_reader):
    """Test update of members."""
    client = owner.login(client)
    data = {
        "members": [{"type": "user", "id": str(public_reader.id)}],
        "visible": False,
        "role": "curator",
    }
    r = client.put(
        f'/communities/{community_id}/members',
        headers=headers,
        json=data,
    )
    assert r.status_code == 204


#
# Delete
#
def test_delete(
        client, headers, community_id, owner, public_reader):
    """Test delete of members."""
    client = public_reader.login(client)
    data = {
        "members": [{"type": "user", "id": str(public_reader.id)}],
    }
    r = client.delete(
        f'/communities/{community_id}/members',
        headers=headers,
        json=data,
    )
    assert r.status_code == 204


#
# Search and serialization
#
def test_search(
        client, headers, community_id, owner, public_reader, db, clean_index):
    """Search."""
    client = owner.login(client)
    r = client.get(
        f'/communities/{community_id}/members',
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json
    assert data['hits']['total'] == 2
    assert 'role' in data['aggregations']
    assert 'visibility' in data['aggregations']

    hit = data['hits']['hits'][0]
    assert 'role' in hit
    assert 'visible' in hit
    assert 'created' in hit
    assert 'updated' in hit
    assert 'revision_id' in hit
    assert 'is_current_user' in hit


def test_search_public(
        client, headers, community_id, new_user, public_reader, clean_index):
    """Search public members."""
    client = new_user.login(client)
    r = client.get(
        f'/communities/{community_id}/members/public',
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json
    assert data['hits']['total'] == 1
    hit = data['hits']['hits'][0]
    # Public view has no facets (because that would leak information on
    # roles/visible)
    assert 'aggregations' not in data
    # A member in the public view should not leak below attributes:
    assert 'role' not in hit
    assert 'visible' not in hit
    assert 'created' not in hit
    assert 'updated' not in hit
    assert 'revision_id' not in hit
    assert 'is_current_user' not in hit
    # A member do have:
    assert 'member' in hit
    assert 'id' in hit['member']
    assert 'type' in hit['member']
    assert 'name' in hit['member']
    assert 'description' in hit['member']


# TODO: member serialization/links
# TODO: request serialization/links
# TODO: community member can see info
# TODO: community non-member can't see info
# TODO: facet by role, facet by visibility, define sorts.
# TODO: same user can be invited to two different communities
# TODO: same user/group can be added to two different communities
