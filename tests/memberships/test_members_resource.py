# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community invitations service."""

import pytest
from flask_principal import Identity, UserNeed
from flask_security import login_user
from invenio_access import any_user, authenticated_user
from invenio_accounts.testutils import create_test_user, login_user_via_session

from invenio_communities.members import Member


# Helpers

def identity_of(user):
    """Dirty way to fake a basic authenticated user identity for user."""
    identity = Identity(user.id)
    identity.provides.add(UserNeed(user.id))
    identity.provides.add(any_user)
    identity.provides.add(authenticated_user)
    return identity


def assert_item_response(response, code=200, body_override=None):
    assert response.status_code == code
    r_json = response.json
    r_json.pop("created")
    r_json.pop("updated")
    expected = {
        # TODO when UserService is integrated
        # "member": {
        #     "user": f"{user_1.id}", # str on purpose
        #     "name": "Lars Holm Nielsen",
        #     "description": "CERN",
        #     "links": {
        #         "self": "",
        #         "self_html": "",
        #         "avatar": "",
        #     }
        # },
        "is_current_user": False,
        # "visibility": "public",  # TODO in #392
        "role": "reader",
        'revision_id': 1,
    }
    expected.update(body_override)
    assert expected == r_json


def logged_client(client, user):
    """Log in a user to the client."""
    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)
    return client


# Fixtures

@pytest.fixture()
def user_1(app, db):
    """Community owner user."""
    return create_test_user('user_1@example.com')


@pytest.fixture()
def user_2(app, db):
    """A non-community affiliated user."""
    return create_test_user('user_2@example.com')


@pytest.fixture()
def user_3(app, db):
    """A non-community affiliated user."""
    return create_test_user('user_3@example.com')


@pytest.fixture()
def owner(app, db):
    """Owner."""
    return create_test_user('owner@example.com')


@pytest.fixture()
def community(community_creation_input_data, community_service, owner):
    """Community data-layer object."""
    community = community_service.create(
        identity_of(owner),
        community_creation_input_data
    )._record
    Member.index.refresh()
    return community


@pytest.fixture()
def private_community(community_creation_input_data, community_service, owner):
    """Private community data-layer object."""
    data = {
        **community_creation_input_data,
        "access": {
            "visibility": "restricted",
            "member_policy": "closed",
            "record_policy": "closed",
        },
        "id": "my_private_community_id",
    }
    community = community_service.create(
        identity_of(owner),
        data
    )._record
    Member.index.refresh()
    return community


# Tests


def test_read_member(
        user_1, client, community, community_service,
        generate_invitation_input_data, headers, make_member_identity, owner):
    community_id = community.pid.pid_value  # id on the URL
    # community_uuid = str(community.id)  # id in the DB
    # another_user_id = str(user_1.id)
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), community, "owner"
    )
    membership = community_service.members.create(
        owner_identity,
        data={
            "community": str(community.id),
            "user": user_1.id,
            "role": "reader"
        }
    )._record
    Member.index.refresh()
    client = logged_client(client, owner)

    r = client.get(
        f'/communities/{community_id}/members/{membership.id}',
        headers=headers,
    )

    override = {
        "id": f"{membership.id}",
        "links": {
            "self": f"https://127.0.0.1:5000/api/communities/{community_id}/members/{membership.id}"  # noqa
        },
    }
    assert_item_response(r, body_override=override)


def test_bulk_update_members(
        user_1, client, community, community_service,
        headers, make_member_identity, owner):
    community_id = community.pid.pid_value  # id on the URL
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), community, "owner"
    )
    membership = community_service.members.create(
        owner_identity,
        data={
            "community": str(community.id),
            "user": user_1.id,
            "role": "reader"
        }
    )._record
    Member.index.refresh()
    client = logged_client(client, owner)
    bulk_update_json = {
        "members": [
            {"id": membership.id, "revision_id": 1}
        ],
        "role": "curator"
    }

    r = client.patch(
        f'/communities/{community_id}/members',
        headers=headers,
        json=bulk_update_json
    )

    assert r.status_code == 204
    assert r.headers["Location"] == f"https://127.0.0.1:5000/api/communities/{community_id}/members"  # noqa
    assert not r.json

    r = client.get(
        f'/communities/{community_id}/members/{membership.id}',
        headers=headers,
    )
    override = {
        "id": f"{membership.id}",
        "role": "curator",
        "links": {
            "self": f"https://127.0.0.1:5000/api/communities/{community_id}/members/{membership.id}"  # noqa
        },
        'revision_id': 2,
    }
    assert_item_response(r, body_override=override)


def test_bulk_update_members_errors(
        user_1, client, private_community, community_service,
        headers, make_member_identity, owner, user_2):
    community_id = private_community.pid.pid_value  # id on the URL
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), private_community, "owner"
    )
    membership = community_service.members.create(
        owner_identity,
        data={
            "community": str(private_community.id),
            "user": user_1.id,
            "role": "reader"
        }
    )._record
    Member.index.refresh()

    # A non-member calling endpoint of private community should get 404
    # (to not reveal community)
    client = logged_client(client, user_2)
    r = client.patch(
        f'/communities/{community_id}/members',
        headers=headers,
        json={}  # Permission should be denied first
    )
    assert r.status_code == 404

    # An invalid request body cancels the update and returns 400
    bulk_update_json = {
        "members": [
            {"foo": "bar"},
            {"id": membership.id, "revision_id": 1}
        ],
        "role": "curator"
    }
    client = logged_client(client, owner)
    r = client.patch(
        f'/communities/{community_id}/members',
        headers=headers,
        json=bulk_update_json
    )
    assert r.status_code == 400
    r = client.get(
        f'/communities/{community_id}/members/{membership.id}',
        headers=headers,
    )
    override = {
        "id": f"{membership.id}",
        "links": {
            "self": f"https://127.0.0.1:5000/api/communities/{community_id}/members/{membership.id}"  # noqa
        },
    }
    assert_item_response(r, body_override=override)

    # An invalid revision_id cancels the update and returns 412
    bulk_update_json = {
        "members": [
            {"id": membership.id, "revision_id": 0}
        ],
        "role": "curator"
    }
    client = logged_client(client, owner)
    r = client.patch(
        f'/communities/{community_id}/members',
        headers=headers,
        json=bulk_update_json
    )
    assert r.status_code == 412
    r = client.get(
        f'/communities/{community_id}/members/{membership.id}',
        headers=headers,
    )
    assert_item_response(r, body_override=override)

    # A permission-wise incompatible update cancels the update and returns 403
    owner_membership = community_service.members.get_member(
        str(private_community.id), owner.id
    )
    bulk_update_json = {
        "members": [
            {"id": owner_membership.id, "revision_id": 1}
        ],
        "role": "curator"
    }
    client = logged_client(client, owner)
    r = client.patch(
        f'/communities/{community_id}/members',
        headers=headers,
        json=bulk_update_json
    )
    assert r.status_code == 403
    r = client.get(
        f'/communities/{community_id}/members/{owner_membership.id}',
        headers=headers,
    )
    override = {
        "id": f"{owner_membership.id}",
        "is_current_user": True,
        "links": {
            "self": f"https://127.0.0.1:5000/api/communities/{community_id}/members/{owner_membership.id}"  # noqa
        },
        "role": "owner"
    }
    assert_item_response(r, body_override=override)


def test_bulk_delete_members(
        user_1, user_2, client, community, community_service, headers,
        make_member_identity, owner):
    community_id = community.pid.pid_value  # id on the URL
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), community, "owner"
    )
    membership_1 = community_service.members.create(
        owner_identity,
        data={
            "community": str(community.id),
            "user": user_1.id,
            "role": "reader"
        }
    )._record
    membership_2 = community_service.members.create(
        owner_identity,
        data={
            "community": str(community.id),
            "user": user_2.id,
            "role": "curator"
        }
    )._record
    Member.index.refresh()
    client = logged_client(client, owner)
    bulk_delete_json = {
        "members": [
            {"id": membership_1.id, "revision_id": 1},
            {"id": membership_2.id, "revision_id": 1}
        ]
    }

    r = client.delete(
        f'/communities/{community_id}/members',
        headers=headers,
        json=bulk_delete_json
    )

    assert r.status_code == 204
    assert not r.json

    r = client.get(
        f'/communities/{community_id}/members/{membership_1.id}',
        headers=headers,
    )
    assert 404 == r.status_code
    r = client.get(
        f'/communities/{community_id}/members/{membership_2.id}',
        headers=headers,
    )
    assert 404 == r.status_code


def test_bulk_delete_members_errors(
        user_1, user_2, user_3, client, private_community, community_service,
        headers, make_member_identity, owner):
    community_id = private_community.pid.pid_value  # id on the URL
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), private_community, "owner"
    )
    membership_1 = community_service.members.create(
        owner_identity,
        data={
            "community": str(private_community.id),
            "user": user_1.id,
            "role": "reader"
        }
    )._record
    membership_2 = community_service.members.create(
        owner_identity,
        data={
            "community": str(private_community.id),
            "user": user_2.id,
            "role": "curator"
        }
    )._record
    Member.index.refresh()

    # A non-member calling endpoint of private community should get 404
    # (to not reveal community)
    client = logged_client(client, user_3)
    r = client.delete(
        f'/communities/{community_id}/members',
        headers=headers,
        json={}  # Permission should be denied first
    )
    assert r.status_code == 404

    # An invalid request body cancels the whole delete and returns 400
    bulk_delete_json = {
        "members": [
            {"id": membership_1.id, "revision_id": 1},
            {"foo": "bar"},
        ],
    }
    client = logged_client(client, owner)
    r = client.delete(
        f'/communities/{community_id}/members',
        headers=headers,
        json=bulk_delete_json
    )
    assert r.status_code == 400
    r = client.get(
        f'/communities/{community_id}/members/{membership_1.id}',
        headers=headers,
    )
    override = {
        "id": f"{membership_1.id}",
        "links": {
            "self": f"https://127.0.0.1:5000/api/communities/{community_id}/members/{membership_1.id}"  # noqa
        },
    }
    assert_item_response(r, body_override=override)

    # An invalid revision_id cancels the whole delete and returns 412
    bulk_delete_json = {
        "members": [
            {"id": membership_1.id, "revision_id": 0},
            {"id": membership_2.id, "revision_id": 1}
        ]
    }
    client = logged_client(client, owner)
    r = client.delete(
        f'/communities/{community_id}/members',
        headers=headers,
        json=bulk_delete_json
    )
    assert r.status_code == 412
    r = client.get(
        f'/communities/{community_id}/members/{membership_2.id}',
        headers=headers,
    )
    override = {
        "id": f"{membership_2.id}",
        "links": {
            "self": f"https://127.0.0.1:5000/api/communities/{community_id}/members/{membership_2.id}"  # noqa
        },
        "role": "curator"
    }
    assert_item_response(r, body_override=override)

    # Attempting to delete last owner cancels whole delete and returns 400
    owner_membership = community_service.members.get_member(
        str(private_community.id), owner.id
    )
    bulk_delete_json = {
        "members": [
            {"id": owner_membership.id, "revision_id": 1}
        ]
    }
    client = logged_client(client, owner)
    r = client.delete(
        f'/communities/{community_id}/members',
        headers=headers,
        json=bulk_delete_json
    )
    assert 400 == r.status_code
    r = client.get(
        f'/communities/{community_id}/members/{owner_membership.id}',
        headers=headers,
    )
    override = {
        "id": f"{owner_membership.id}",
        "is_current_user": True,
        "links": {
            "self": f"https://127.0.0.1:5000/api/communities/{community_id}/members/{owner_membership.id}"  # noqa
        },
        "role": "owner"
    }
    assert_item_response(r, body_override=override)
