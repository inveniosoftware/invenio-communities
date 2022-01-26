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
from invenio_access.permissions import system_identity
from invenio_accounts.testutils import create_test_user
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_requests_service
from sqlalchemy.orm.exc import NoResultFound

from invenio_communities.members import AlreadyMemberError, LastOwnerError, \
    ManagerSelfRoleChangeError, Member, OwnerSelfRoleChangeError


# Fixtures

@pytest.fixture(scope="module")
def another_user(app):
    """Community owner user."""
    return create_test_user('another_user@example.com')


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


# Tests

def test_invite_user_flow(
        another_identity, community_creation_input_data,
        community_service, create_user_identity,
        generate_invitation_input_data, make_member_identity,
        requests_service):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    community_id = str(community.id)
    owner_identity = make_member_identity(owner_identity, community, "owner")
    user_id = str(another_identity.id)

    # Invite
    data = generate_invitation_input_data(
        community_id, {"user": user_id}, "reader"
    )
    invitation = community_service.invitations.create(owner_identity, data)

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
        owner_identity,
        community_id,
        extra_filter=Q('term', community_id=community_id),
    )

    member_dict = next(members.hits, None)
    assert member_dict["id"]
    assert "reader" == member_dict["role"]


@pytest.fixture()
def get_membership_id(community_service):
    """Get membership."""

    def _get_membership_id(community_id, user_id):
        """Wrapped."""
        members = community_service.members.search(
            system_identity,
            community_id,
            extra_filter=(
                Q('term', community_id=community_id) &
                Q('term', user_id=user_id)
            )
        )
        member_dict = next(members.hits, None)
        return member_dict["id"]

    return _get_membership_id


def test_owner_can_leave_if_at_least_1_other_owner(
        create_user_identity, community_service, community_creation_input_data,
        get_membership_id, make_member_identity):
    owner_identity = create_user_identity("owner@example.com")
    # Creating a community also creates an owner membership
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    Member.index.refresh()
    owner_identity = make_member_identity(owner_identity, community, "owner")
    membership_id = get_membership_id(community.id, owner_identity.id)

    # Sole owner can't leave
    with pytest.raises(LastOwnerError):
        community_service.members.delete(owner_identity, membership_id)

    # Add other owner
    owner2_identity = create_user_identity("owner2@example.com")
    owner2_identity = make_member_identity(owner2_identity, community, "owner")
    owner2_membership = community_service.members.create(
        owner_identity,
        data={
            "community": str(community.id),
            "user": owner2_identity.id,
            "role": "owner"
        }
    )._record
    Member.index.refresh()

    # Now owner can leave
    community_service.members.delete(owner_identity, membership_id)

    with pytest.raises(NoResultFound):
        community_service.members.read(owner2_identity, membership_id)


def test_update_role(
        create_user_identity, community_service, community_creation_input_data,
        get_membership_id, make_member_identity):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    Member.index.refresh()
    owner_membership_id = get_membership_id(community.id, owner_identity.id)
    owner_identity = make_member_identity(owner_identity, community, "owner")
    manager_identity = create_user_identity("manager@example.com")
    manager_identity = make_member_identity(
        manager_identity, community, "manager")
    manager_membership = community_service.members.create(
        owner_identity,
        data={
            "community": str(community.id),
            "user": manager_identity.id,
            "role": "manager"
        }
    )._record
    member_identity = create_user_identity("member@example.com")
    member_identity = make_member_identity(member_identity, community)
    membership = community_service.members.create(
        owner_identity,
        data={
            "community": str(community.id),
            "user": member_identity.id,
            "role": "reader"
        }
    )._record
    Member.index.refresh()

    # Owner and Manager can edit role of any other member
    ## Owner can
    community_service.members.update(
        owner_identity,
        membership.id,
        data={
            "community": str(community.id),
            "user": member_identity.id,
            "role": "curator"
        }
    )

    membership_result = community_service.members.read(
        owner_identity, membership.id
    )
    assert "curator" == membership_result.to_dict()["role"]

    ## Manager can
    community_service.members.update(
        manager_identity,
        membership.id,
        data={
            "community": str(community.id),
            "user": member_identity.id,
            "role": "reader"
        }
    )

    membership_result = community_service.members.read(
        owner_identity, membership.id
    )
    assert "reader" == membership_result.to_dict()["role"]

    # Owner can't change own role
    with pytest.raises(OwnerSelfRoleChangeError):
        community_service.members.update(
            owner_identity,
            owner_membership_id,
            data={
                "community": str(community.id),
                "user": owner_identity.id,
                "role": "reader"
            }
        )
    # still an owner
    membership_result = community_service.members.read(
        owner_identity, owner_membership_id
    )
    assert "owner" == membership_result.to_dict()["role"]

    # Manager can't change own role
    with pytest.raises(ManagerSelfRoleChangeError):
        community_service.members.update(
            manager_identity,
            manager_membership.id,
            data={
                "community": str(community.id),
                "user": manager_identity.id,
                "role": "reader"
            }
        )
    # still a manager
    membership_result = community_service.members.read(
        owner_identity, manager_membership.id
    )
    assert "manager" == membership_result.to_dict()["role"]

    # Manager cannot change role of owner
    with pytest.raises(PermissionDeniedError):
        community_service.members.update(
            manager_identity,
            owner_membership_id,
            data={
                "community": str(community.id),
                "user": owner_identity.id,
                "role": "reader"
            }
        )
    # still an owner
    membership_result = community_service.members.read(
        owner_identity, owner_membership_id
    )
    assert "owner" == membership_result.to_dict()["role"]



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
