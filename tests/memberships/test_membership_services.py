# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community invitations service."""

import pytest
from elasticsearch_dsl.query import Q
from flask_principal import Identity, Need, UserNeed
from invenio_accounts.testutils import create_test_user
from invenio_requests import current_requests_service

from invenio_communities.proxies import current_communities
from invenio_communities.members import AlreadyMemberError, Member

# Fixtures

@pytest.fixture(scope="module")
def community_owner(app):
    """Community owner user."""
    return create_test_user('community-owner@inveniosoftware.org')


@pytest.fixture(scope="module")
def another_user(app):
    """Community owner user."""
    return create_test_user('another_user@example.com')


@pytest.fixture(scope="module")
def community_owner_identity(community_owner):
    """Simple identity fixture."""
    owner_id = community_owner.id
    i = Identity(owner_id)
    i.provides.add(UserNeed(owner_id))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture(scope="module")
def another_identity(another_user):
    """Simple identity fixture."""
    user_id = another_user.id
    i = Identity(user_id)
    i.provides.add(UserNeed(user_id))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture(scope="module")
def community_creation_input_data():
    """Full community data used as input to community service."""
    return  {
        "access": {
            "visibility": "public",
            "member_policy": "open",
            "record_policy": "open",
        },
        "id": "my_community_id",
        "metadata": {
            "title": "My Community",
            "description": "This is an example Community.",
            "type": "event",
            "curation_policy": "This is the kind of records we accept.",
            "website": "https://inveniosoftware.org/",
            "organizations": [{
                    "name": "CERN",
            }]
        }
    }


@pytest.fixture(scope="function")
def community_service(app, location):
    """Community service.

    Snuck in the location fixture, because needed on community creation
    i.e. almost every time this service is used.
    """
    return current_communities.service


@pytest.fixture(scope="module")
def requests_service(app):
    """Requests service."""
    return current_requests_service


@pytest.fixture(scope="function")
def community(community_service, community_owner_identity,
              community_creation_input_data):
    """Community fixture."""
    return community_service.create(
        community_owner_identity, community_creation_input_data
    )


@pytest.fixture()
def invitation_creation_input_data(another_user, community):
    """Full invitation data used as input to invitation service."""
    return {
        "type": "community-member-invitation",
        "receiver": {"user": another_user.id},
        "payload": {
            "role": "reader",
        },
        # Added by resource
        "topic": {'community': community.data['uuid']}
    }


# Tests

def test_invite_user_flow(
        another_identity, community, community_owner_identity,
        community_service, invitation_creation_input_data,
        requests_service):
    community_id = community.data['uuid']
    user_id = str(another_identity.id)

    # Invite
    invitation = community_service.invitations.create(
        community_owner_identity, invitation_creation_input_data
    )

    invitation_dict = invitation.to_dict()
    assert 'open' == invitation_dict['status']
    assert invitation_dict['is_open'] is True
    assert {'community': community_id} == invitation_dict['topic']
    assert {'user': user_id} == invitation_dict['receiver']
    assert {'community': community_id} == invitation_dict['created_by']
    assert 'reader' == invitation_dict["payload"]['role']

    # Accept
    invitation = requests_service.execute_action(
        another_identity, invitation.id, 'accept', {}
    )

    invitation_dict = invitation.to_dict()
    assert 'accepted' == invitation_dict['status']
    assert invitation_dict['is_open'] is False
    assert invitation_dict['is_closed'] is True

    Member.index.refresh()

    # Get membership
    members = community_service.members.search(
        community_owner_identity,
        extra_filter=Q('term', community_id=community_id),
    )

    member_dict = next(members.hits, None)
    assert member_dict["id"]
    assert "reader" == member_dict["role"]

    # Invite accepted fails
    with pytest.raises(AlreadyMemberError) as e:
        community_service.invitations.create(
            community_owner_identity, invitation_creation_input_data
        )


# TODO
# test can't invite already invited (not accepted/declined/cancelled yet)
# test read invitation
# test decline
# test cancel
# test commenting on invitation
# test remove member from communities
# test search invitations
# test read member result_item .to_dict() for member read(1)
# - community member can see info
# - community non-member can't see info
# test search members
# - community member can see info
# - community non-member can't see info
# test add member directly programmatically
