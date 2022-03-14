# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community invitations service."""

from copy import deepcopy

import pytest
from flask_principal import Identity, UserNeed
from flask_security import login_user
from invenio_access import any_user, authenticated_user
from invenio_accounts.testutils import create_test_user, login_user_via_session
from invenio_requests.records import Request

from invenio_communities.members import Member


# Fixtures


@pytest.fixture()
def another_user(app, db):
    """Community owner user."""
    return create_test_user('another_user@example.com')


@pytest.fixture()
def owner(app, db):
    """Owner."""
    return create_test_user('owner@example.com')


def identity_of(user):
    """Dirty way to fake a basic authenticated user identity for user."""
    identity = Identity(user.id)
    identity.provides.add(UserNeed(user.id))
    identity.provides.add(any_user)
    identity.provides.add(authenticated_user)
    return identity


@pytest.fixture()
def community(community_creation_input_data, community_service, owner):
    """Community data-layer object."""
    community = community_service.create(
        identity_of(owner),
        community_creation_input_data
    )._record
    Member.index.refresh()
    return community


def logged_client(client, user):
    """Log in a user to the client."""
    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)
    return client


# Tests


def assert_links(community_id, invitation_id, received_links):
    """Assert received are as expected"""
    prefix = "https://127.0.0.1:5000/api/communities"
    links = {
        "actions": {
            "accept": f"{prefix}/{community_id}/invitations/{invitation_id}/actions/accept",
            "cancel": f"{prefix}/{community_id}/invitations/{invitation_id}/actions/cancel",
            "decline": f"{prefix}/{community_id}/invitations/{invitation_id}/actions/decline",
            "expire": f"{prefix}/{community_id}/invitations/{invitation_id}/actions/expire",
        },
        # TODO "comments" in #398
        "self": f"{prefix}/{community_id}/invitations/{invitation_id}"
    }
    assert links == received_links


def test_create_and_get_invitation(
        another_user, client, community, generate_invitation_input_data,
        headers, owner):
    community_id = community.pid.pid_value  # id on the URL
    community_uuid = str(community.id)  # id in the DB
    another_user_id = str(another_user.id)
    invitation_input_data = generate_invitation_input_data(
        community_uuid, {"user": another_user_id}, role="reader"
    )
    client = logged_client(client, owner)

    r = client.post(
        f'/communities/{community_id}/invitations',
        headers=headers,
        json=invitation_input_data
    )

    assert r.status_code == 201
    r_json = r.json
    assert "open" == r_json["status"]
    assert "Invitation to join \"My Community\" as reader" == r_json["title"]
    assert "community-member-invitation" == r_json["type"]
    assert community_uuid == r_json["created_by"]["community"]
    assert another_user_id == r_json["receiver"]["user"]
    assert community_uuid == r_json["topic"]["community"]
    assert {"role": "reader"} == r_json["payload"]
    invitation_id = r_json["id"]
    assert_links(community_id, invitation_id, r_json["links"])

    r = client.get(
        f'/communities/{community_id}/invitations/{invitation_id}',
        headers=headers,
    )

    assert r.status_code == 200
    r_json = r.json
    assert "open" == r_json["status"]
    assert "Invitation to join \"My Community\" as reader" == r_json["title"]
    assert "community-member-invitation" == r_json["type"]
    assert community_uuid == r_json["created_by"]["community"]
    assert another_user_id == r_json["receiver"]["user"]
    assert community_uuid == r_json["topic"]["community"]
    assert {"role": "reader"} == r_json["payload"]
    assert_links(community_id, invitation_id, r_json["links"])


def test_modify_invitation_role(
        another_user, client, community, community_service,
        generate_invitation_input_data, headers, make_member_identity, owner):
    community_id = community.pid.pid_value  # id on the URL
    community_uuid = str(community.id)  # id in the DB
    another_user_id = str(another_user.id)
    invitation_input_data = generate_invitation_input_data(
        community_uuid, {"user": another_user_id}, role="reader"
    )
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), community, "owner"
    )
    invitation = community_service.invitations.create(
        owner_identity, invitation_input_data
    )
    invitation_id = str(invitation.id)
    client = logged_client(client, owner)

    # Can modify role
    data = deepcopy(invitation.data)
    data["payload"]["role"] = "curator"
    r = client.put(
        f'/communities/{community_id}/invitations/{invitation_id}',
        headers=headers,
        json=data
    )

    assert r.status_code == 200
    r_json = r.json
    assert "curator" == r_json["payload"]["role"]
    assert_links(community_id, invitation_id, r_json["links"])


def assert_no_actions_links(community_id, invitation_id, received_links):
    """Assert no actions links."""
    prefix = "https://127.0.0.1:5000/api/communities"
    links = {
        "actions": {},
        # TODO "comments" in #398
        "self": f"{prefix}/{community_id}/invitations/{invitation_id}"
    }
    assert links == received_links


def test_cancel_invitation(
        another_user, client, community, community_service,
        generate_invitation_input_data, headers, make_member_identity, owner):
    community_id = community.pid.pid_value  # id on the URL
    community_uuid = str(community.id)  # id in the DB
    another_user_id = str(another_user.id)
    invitation_input_data = generate_invitation_input_data(
        community_uuid, {"user": another_user_id}, role="reader"
    )
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), community, "owner"
    )
    invitation = community_service.invitations.create(
        owner_identity, invitation_input_data
    )
    invitation_id = str(invitation.id)
    client = logged_client(client, owner)

    r = client.post(
        f'/communities/{community_id}/invitations/{invitation_id}/actions/cancel',  # noqa
        headers=headers,
    )

    assert r.status_code == 200
    r_json = r.json
    assert "cancelled" == r_json["status"]
    assert_no_actions_links(community_id, invitation_id, r_json["links"])


def test_accept_invitation(
        another_user, client, community, community_service,
        generate_invitation_input_data, headers, make_member_identity, owner):
    community_id = community.pid.pid_value  # id on the URL
    community_uuid = str(community.id)  # id in the DB
    another_user_id = str(another_user.id)
    invitation_input_data = generate_invitation_input_data(
        community_uuid, {"user": another_user_id}, role="reader"
    )
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), community, "owner"
    )
    invitation = community_service.invitations.create(
        owner_identity, invitation_input_data
    )
    invitation_id = str(invitation.id)
    client = logged_client(client, another_user)

    r = client.post(
        f'/communities/{community_id}/invitations/{invitation_id}/actions/accept',  # noqa
        headers=headers,
    )

    assert r.status_code == 200
    r_json = r.json
    assert "accepted" == r_json["status"]
    assert_no_actions_links(community_id, invitation_id, r_json["links"])


def test_decline_invitation(
        another_user, client, community, community_service,
        generate_invitation_input_data, headers, make_member_identity, owner):
    community_id = community.pid.pid_value  # id on the URL
    community_uuid = str(community.id)  # id in the DB
    another_user_id = str(another_user.id)
    invitation_input_data = generate_invitation_input_data(
        community_uuid, {"user": another_user_id}, role="reader"
    )
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), community, "owner"
    )
    invitation = community_service.invitations.create(
        owner_identity, invitation_input_data
    )
    invitation_id = str(invitation.id)
    client = logged_client(client, another_user)

    r = client.post(
        f'/communities/{community_id}/invitations/{invitation_id}/actions/decline',  # noqa
        headers=headers,
    )

    assert r.status_code == 200
    r_json = r.json
    assert "declined" == r_json["status"]
    assert_no_actions_links(community_id, invitation_id, r_json["links"])


# TODO: Should it be possible to expire via API? I dont't think so.
#       But then there should be a way to prevent for that.


@pytest.fixture()
def yet_another_user(app, db):
    """Community owner user."""
    return create_test_user('yet_another_user@example.com')


def test_search_invitations(
        another_user, client, community, community_service,
        generate_invitation_input_data, headers, make_member_identity, owner,
        yet_another_user):
    # we have to give them the owner identity in tests
    owner_identity = make_member_identity(
        identity_of(owner), community, "owner"
    )
    community_id = community.pid.pid_value  # id on the URL
    community_uuid = str(community.id)  # id in the DB
    user_id_1 = str(another_user.id)
    # Create an open invitation
    invitation_input_data = generate_invitation_input_data(
        community_uuid, {"user": user_id_1}, role="reader"
    )
    invitation1 = community_service.invitations.create(
        owner_identity, invitation_input_data
    )
    # Create a closed invitation by cancelling a new invitation
    user_id_2 = str(yet_another_user.id)
    invitation_input_data = generate_invitation_input_data(
        community_uuid, {"user": user_id_2}, role="reader"
    )
    invitation2 = community_service.invitations.create(
        owner_identity, invitation_input_data
    )
    community_service.invitations.execute_action(
        owner_identity, community_id, invitation2.id, "cancel"
    )
    Request.index.refresh()
    client = logged_client(client, owner)

    # By default all invitations are returned
    r = client.get(
        f'/communities/{community_id}/invitations',
        headers=headers,
    )
    assert r.status_code == 200
    r_json = r.json
    assert r_json["hits"]["total"] == 2
    links = {
        "self": f"https://127.0.0.1:5000/api/communities/{community_id}/invitations?page=1&size=25&sort=newest"  # noqa
    }
    assert links == r_json["links"]

    # Filter for open invitations
    r = client.get(
        f'/communities/{community_id}/invitations',
        query_string={'status': "open"},
        headers=headers,
    )
    assert r.status_code == 200
    r_json = r.json
    assert r_json["hits"]["total"] == 1

    # Filter for cancelled invitations
    r = client.get(
        f'/communities/{community_id}/invitations',
        query_string={'status': "cancelled"},
        headers=headers,
    )
    assert r.status_code == 200
    r_json = r.json
    assert r_json["hits"]["total"] == 1
