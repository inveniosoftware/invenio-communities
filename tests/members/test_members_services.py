# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community member service."""

import pytest
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.records.api import RequestEvent
from marshmallow import ValidationError

from invenio_communities.members.errors import AlreadyMemberError, InvalidMemberError
from invenio_communities.members.records.api import ArchivedInvitation, Member


#
# Add members
#
@pytest.mark.parametrize(
    "actor,role",
    [
        ("owner", "owner"),
        ("owner", "manager"),
        ("owner", "curator"),
        ("owner", "reader"),
        ("manager", "manager"),
        ("manager", "curator"),
        ("manager", "reader"),
    ],
)
def test_add_allowed(member_service, community, members, group, actor, role, db):
    """Test that the given roles CAN add a group member."""
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": role,
    }
    member_service.add(members[actor].identity, community._record.id, data)


@pytest.mark.parametrize(
    "actor,role",
    [
        ("manager", "owner"),
        ("curator", "owner"),
        ("curator", "manager"),
        ("curator", "curator"),
        ("curator", "reader"),
        ("reader", "owner"),
        ("reader", "manager"),
        ("reader", "curator"),
        ("reader", "reader"),
    ],
)
def test_add_denied(member_service, community, members, group, actor, role, db):
    """Test that the given roles CANNOT add a group member."""
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": role,
    }
    assert pytest.raises(
        PermissionDeniedError,
        member_service.add,
        members[actor].identity,
        community._record.id,
        data,
    )


def test_add_duplicate(member_service, community, owner, group, db):
    """Test that we cannot add duplicate members."""
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
    }
    member_service.add(owner.identity, community._record.id, data)
    data["role"] = "curator"
    # Duplicate detected (even if role changed)
    assert pytest.raises(
        AlreadyMemberError,
        member_service.add,
        owner.identity,
        community._record.id,
        data,
    )


def test_add_invalid_member_type(member_service, community, owner, new_user, db):
    """Only system identity can add a denied member type."""
    data = {
        # "type: user" is allowed to add only by system
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    assert pytest.raises(
        PermissionDeniedError,
        member_service.add,
        owner.identity,
        community._record.id,
        data,
    )
    member_service.add(system_identity, community._record.id, data)


def test_add_visible_property(member_service, community, owner, new_user, db):
    """Only system identity can set visible property."""
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
        # visible allowed only to be set by system.
        "visible": True,
    }
    assert pytest.raises(
        ValidationError, member_service.add, owner.identity, community._record.id, data
    )
    member_service.add(system_identity, community._record.id, data)


def test_add_invalid_data(member_service, community, owner, group, db):
    """Test various forms of invalid data."""
    # Invalid group id
    data = {"members": [{"type": "group", "id": "invalid"}], "role": "reader"}
    assert pytest.raises(
        InvalidMemberError,
        member_service.add,
        owner.identity,
        community._record.id,
        data,
    )
    # Missing member id
    data = {"members": [{"type": "group"}], "role": "reader"}
    assert pytest.raises(
        ValidationError, member_service.add, owner.identity, community._record.id, data
    )
    # Missing member type
    data = {"members": [{"id": "groupname"}], "role": "reader"}
    assert pytest.raises(
        ValidationError, member_service.add, owner.identity, community._record.id, data
    )
    # Invalid member type
    data = {"members": [{"type": "invalid", "id": "1"}], "role": "reader"}
    assert pytest.raises(
        ValidationError, member_service.add, owner.identity, community._record.id, data
    )
    # No members
    data = {"members": [], "role": "reader"}
    assert pytest.raises(
        Exception, member_service.add, owner.identity, community._record.id, data
    )
    # Invalid role
    data = {"members": [{"type": "group", "id": group.name}], "role": "inval"}
    assert pytest.raises(
        ValidationError, member_service.add, owner.identity, community._record.id, data
    )
    # Cannot add email
    data = {
        "members": [{"type": "email", "id": "somebody@somewhere.org"}],
        "role": "reader",
    }
    assert pytest.raises(
        ValidationError,
        # using system_identity because owner gets a permission denied before
        # validation kicks in.
        member_service.add,
        system_identity,
        community._record.id,
        data,
    )


#
# Invite members
#
def test_invite(member_service, community, owner, new_user, db):
    """Invite a user."""
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.invite(owner.identity, community._record.id, data)
    # ensure that the invited user request has been indexed
    res = member_service.search_invitations(
        owner.identity, community._record.id
    ).to_dict()
    assert res["hits"]["total"] == 1
    # Cannot invite twice.
    pytest.raises(
        AlreadyMemberError,
        member_service.invite,
        owner.identity,
        community._record.id,
        data,
    )
    # Cannot add either if invited
    pytest.raises(
        AlreadyMemberError,
        member_service.add,
        system_identity,
        community._record.id,
        data,
    )


def test_invite_group_denied(member_service, community, owner, group, db):
    """Invite a group."""
    # Groups cannot be invited (groups cannot receive invitation request)
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
    }
    # - owner identity
    assert pytest.raises(
        PermissionDeniedError,
        member_service.invite,
        owner.identity,
        community._record.id,
        data,
    )
    # - system identity
    assert pytest.raises(
        InvalidMemberError,
        member_service.invite,
        system_identity,
        community._record.id,
        data,
    )
    # Email invitations not yet implemented
    data["members"][0]["type"] = "email"
    assert pytest.raises(
        ValidationError,
        member_service.invite,
        owner.identity,
        community._record.id,
        data,
    )


def test_invite_already_member(member_service, community, owner, new_user, db):
    """Invite a user."""
    res = member_service.search(owner.identity, community._record.id).to_dict()
    current = res["hits"]["total"]

    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.add(system_identity, community._record.id, data)
    res = member_service.search(owner.identity, community._record.id).to_dict()
    assert res["hits"]["total"] == current + 1
    # Cannot invite if already a member.
    pytest.raises(
        AlreadyMemberError,
        member_service.invite,
        owner.identity,
        community._record.id,
        data,
    )


def test_invite_with_message(member_service, community, owner, new_user, db):
    """Invite a user."""
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
        "message": "Welcome to the club!",
    }
    assert member_service.invite(owner.identity, community._record.id, data)
    # Invalid message
    data["message"] = 1
    pytest.raises(
        ValidationError,
        member_service.invite,
        owner.identity,
        community._record.id,
        data,
    )


def test_invite_view_request(
    events_service, requests_service, invite_user, db, clean_index
):
    """A request should have been created."""
    res = requests_service.search(
        invite_user.identity,
        receiver={"user": invite_user.id},
        type="community-invitation",
    ).to_dict()
    assert res["hits"]["total"] == 1

    # check request comment since invite user has a message
    RequestEvent.index.refresh()
    res = events_service.search(
        invite_user.identity,
        request_id=res["hits"]["hits"][0]["id"],
    ).to_dict()
    hits = res["hits"]
    assert hits["total"] == 2  # role + invitation
    assert hits["hits"][0]["payload"]["content"] == 'You will join as "Reader".'
    assert hits["hits"][1]["payload"]["content"] == "Welcome to the club!"


#
# Search and read members
#
def test_search_members(
    member_service, community, owner, public_reader, anon_identity, clean_index
):
    """Members can see all members, anyone can only see public."""
    # Members can see all other members.
    res = member_service.search(owner.identity, community._record.id)
    assert res.to_dict()["hits"]["total"] == 2
    # search on the affiliation (tests query expansion)
    res = member_service.search(
        owner.identity, community._record.id, q=f"affiliation:CERN"
    )
    assert res.to_dict()["hits"]["total"] == 1
    res = member_service.search(owner.identity, community._record.id, q=f"name:New")
    assert res.to_dict()["hits"]["total"] == 1
    res = member_service.search(
        owner.identity, community._record.id, q=f"email:newuser@newuser.org"
    )
    assert res.to_dict()["hits"]["total"] == 1


def test_search_public_members(
    member_service, community, owner, public_reader, anon_identity, clean_index
):
    """Members can see all members, anyone can only see public."""
    # Anyone else can only see public members.
    res = member_service.search_public(anon_identity, community._record.id)
    assert res.to_dict()["hits"]["total"] == 1
    # search on the affiliation (tests query expansion)
    res = member_service.search_public(
        owner.identity, community._record.id, q=f"affiliation:CERN"
    )
    assert res.to_dict()["hits"]["total"] == 1
    res = member_service.search_public(
        owner.identity, community._record.id, q=f"name:New"
    )
    assert res.to_dict()["hits"]["total"] == 1
    # search on private fields should not get hits
    res = member_service.search_public(
        owner.identity, community._record.id, q=f"newuser@newuser.org"
    )
    assert res.to_dict()["hits"]["total"] == 0
    # should get hits if using private search
    res = member_service.search(
        owner.identity, community._record.id, q=f"newuser@newuser.org"
    )
    assert res.to_dict()["hits"]["total"] == 1


def test_search_members_restricted(
    member_service, restricted_community, owner, anon_identity, clean_index
):
    """Restricted communities can only be searched by members."""
    c = restricted_community

    # Members can see all other members.
    res = member_service.search(owner.identity, c._record.id)
    assert res.to_dict()["hits"]["total"] == 1

    # Anyone get permission denied.
    pytest.raises(
        PermissionDeniedError, member_service.search_public, anon_identity, c._record.id
    )


#
# Search invitations
#
def test_search_invitations(
    member_service,
    requests_service,
    community,
    owner,
    invite_user,
    invite_request_id,
    db,
    clean_index,
):
    """Search invitations should include archived invitations."""
    # Decline the invitation and reinvite
    requests_service.execute_action(
        invite_user.identity, invite_request_id, "decline"
    ).to_dict()
    data = {
        "members": [{"type": "user", "id": str(invite_user.id)}],
        "role": "reader",
    }
    member_service.invite(owner.identity, community._record.id, data)

    # See invitations in list
    res = member_service.search_invitations(owner.identity, community._record.id)
    assert res.to_dict()["hits"]["total"] == 2


#
# Accept/decline/cancel invite
#
def test_invite_accept_flow(
    member_service,
    requests_service,
    community,
    owner,
    invite_user,
    invite_request_id,
    db,
    clean_index,
):
    """Invite a user."""
    # Accept request
    request = requests_service.execute_action(
        invite_user.identity, invite_request_id, "accept"
    ).to_dict()

    # See new member in list
    res = member_service.search(owner.identity, community._record.id)
    assert res.to_dict()["hits"]["total"] == 2

    # See invitation in archived list
    ArchivedInvitation.index.refresh()
    res = member_service.search_invitations(owner.identity, community._record.id)
    assert res.to_dict()["hits"]["total"] == 1


def test_invite_decline_flow(
    member_service,
    requests_service,
    community,
    owner,
    invite_user,
    invite_request_id,
    db,
    clean_index,
):
    """Invite a user."""
    # Decline request
    request = requests_service.execute_action(
        invite_user.identity, invite_request_id, "decline"
    ).to_dict()

    # Only owner in list
    Member.index.refresh()
    res = member_service.search(owner.identity, community._record.id)
    assert res.to_dict()["hits"]["total"] == 1

    # It's possible to reinvite
    data = {
        "members": [{"type": "user", "id": str(invite_user.id)}],
        "role": "reader",
    }
    member_service.invite(owner.identity, community._record.id, data)


def test_invite_cancel_flow(
    member_service,
    requests_service,
    community,
    owner,
    invite_request_id,
    db,
    clean_index,
):
    """Invite a user."""
    # Cancel request
    request = requests_service.execute_action(
        owner.identity, invite_request_id, "cancel"
    ).to_dict()

    # Only owner in list
    Member.index.refresh()
    res = member_service.search(owner.identity, community._record.id)
    assert res.to_dict()["hits"]["total"] == 1


def test_invite_actions_permissions(
    requests_service, owner, any_user, members, invite_user, invite_request_id, db
):
    """Actions should be protected."""
    manager = members["manager"]
    curator = members["curator"]
    reader = members["reader"]

    # Only invited user can accept/decline
    for user in [owner, any_user, manager, curator, reader]:
        pytest.raises(
            PermissionDeniedError,
            requests_service.execute_action,
            user.identity,
            invite_request_id,
            "accept",
        )
        pytest.raises(
            PermissionDeniedError,
            requests_service.execute_action,
            user.identity,
            invite_request_id,
            "decline",
        )

    # Only community owners/managers can cancel
    for user in [any_user, curator, reader, invite_user]:
        pytest.raises(
            PermissionDeniedError,
            requests_service.execute_action,
            user.identity,
            invite_request_id,
            "cancel",
        )


#
# Leave community
#
@pytest.mark.parametrize("role", ["manager", "curator", "reader"])
def test_leave_allowed(member_service, community, members, role):
    """Managers, curators and readers can leave."""
    user = members[role]
    data = {"members": [{"type": "user", "id": str(user.id)}]}
    assert member_service.delete(user.identity, community._record.id, data)


def test_leave_single_owner_denied(member_service, community, owner):
    """A single owner cannot leave"""
    data = {"members": [{"type": "user", "id": str(owner.id)}]}
    pytest.raises(
        ValidationError,
        member_service.delete,
        owner.identity,
        community._record.id,
        data,
    )


def test_leave_denied(member_service, community, any_user, invite_user):
    """No permission for others"""
    data = {"members": [{"type": "user", "id": str(any_user.id)}]}
    pytest.raises(
        PermissionDeniedError,
        member_service.delete,
        any_user.identity,
        community._record.id,
        data,
    )
    data = {"members": [{"type": "user", "id": str(invite_user.id)}]}
    pytest.raises(
        PermissionDeniedError,
        member_service.delete,
        invite_user.identity,
        community._record.id,
        data,
    )


def test_leave_owner_allowed(member_service, community, owner, group, db):
    """If multiple owners exists, an owner can leave"""
    # Add an owner
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "owner",
    }
    member_service.add(owner.identity, community._record.id, data)

    # Leave
    data = {"members": [{"type": "user", "id": str(owner.id)}]}
    assert member_service.delete(owner.identity, community._record.id, data)


#
# Delete members
#
# TODO: there should be one user owner (group owner not enough).
@pytest.mark.parametrize(
    "actor,role",
    [
        ("manager", "owner"),
        ("curator", "owner"),
        ("curator", "manager"),
        ("curator", "curator"),
        ("curator", "reader"),
        ("reader", "owner"),
        ("reader", "manager"),
        ("reader", "curator"),
        ("reader", "reader"),
    ],
)
def test_delete_denied(member_service, community, members, actor, new_user, role, db):
    """Test that the given roles CANNOT be removed by the actor."""
    # Add a new user with role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.add(system_identity, community._record.id, data)
    # Delete the user
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
    }
    assert pytest.raises(
        PermissionDeniedError,
        member_service.delete,
        members[actor].identity,
        community._record.id,
        data,
    )


@pytest.mark.parametrize(
    "actor,role",
    [
        ("owner", "owner"),
        ("owner", "manager"),
        ("owner", "curator"),
        ("owner", "reader"),
        ("manager", "manager"),
        ("manager", "curator"),
        ("manager", "reader"),
    ],
)
def test_delete_allowed(member_service, community, members, actor, role, new_user, db):
    """Test that the given roles CAN be removed by the actor."""
    # Add a new user with role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.add(system_identity, community._record.id, data)
    # Delete the member again as the actor
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
    }
    member_service.delete(members[actor].identity, community._record.id, data)


def test_delete_member_type_group(member_service, community, owner, group, db):
    """Groups can be removed."""
    # Add a new user with role
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "reader",
    }
    member_service.add(system_identity, community._record.id, data)
    # Delete the member again
    data = {
        "members": [{"type": "group", "id": group.name}],
    }
    member_service.delete(owner.identity, community._record.id, data)


def test_delete_invalid_member(member_service, community, owner):
    """Invalid members and member types raises an error."""
    data = {"members": [{"type": "group", "id": "invalid"}]}
    pytest.raises(
        InvalidMemberError,
        member_service.delete,
        owner.identity,
        community._record.id,
        data,
    )
    data = {"members": [{"type": "invalid", "id": "1"}]}
    pytest.raises(
        ValidationError,
        member_service.delete,
        owner.identity,
        community._record.id,
        data,
    )


#
# Update self
#
def test_selfupdate_denied(member_service, community, any_user, new_user):
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "visible": False,
    }
    for u in [any_user, new_user]:
        pytest.raises(
            PermissionDeniedError,
            member_service.update,
            u.identity,
            community._record.id,
            data,
        )


@pytest.mark.parametrize(
    "actor",
    [
        "owner",
        "manager",
        "curator",
        "reader",
    ],
)
def test_selfupdate_role_denied(member_service, community, members, actor):
    """Nobody can change their own role."""
    user = members[actor]
    data = {
        "members": [{"type": "user", "id": str(user.id)}],
        "role": actor,
    }
    pytest.raises(
        ValidationError,
        member_service.update,
        user.identity,
        community._record.id,
        data,
    )


@pytest.mark.parametrize(
    "actor",
    [
        "owner",
        "manager",
        "curator",
        "reader",
    ],
)
def test_selfupdate_allow_visibility(member_service, community, members, actor, db):
    """All + system identity can change their own visibility to true."""
    user = members[actor]
    data = {
        "members": [{"type": "user", "id": str(user.id)}],
        "visible": True,
    }
    member_service.update(user.identity, community._record.id, data)
    member_service.update(system_identity, community._record.id, data)


#
# Update members
#
@pytest.mark.parametrize(
    "actor,role",
    [
        ("owner", "owner"),
        ("owner", "manager"),
        ("owner", "curator"),
        ("owner", "reader"),
        ("manager", "manager"),
        ("manager", "curator"),
        ("manager", "reader"),
    ],
)
def test_update_public_visibility_denied(
    member_service, community, members, actor, role, new_user, db
):
    """Only members themselves can set public visibility."""
    # Add a new user with role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.add(system_identity, community._record.id, data)
    # Update the member
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "visible": True,
    }
    pytest.raises(
        ValidationError,
        member_service.update,
        members[actor].identity,
        community._record.id,
        data,
    )


def test_update_public_visibility_of_group_allowed(
    member_service, community, owner, group, db
):
    """Group visibility can always be set to true."""
    # Add a new user with role
    data = {
        "members": [{"type": "group", "id": str(group.name)}],
        "role": "reader",
    }
    member_service.add(system_identity, community._record.id, data)
    # Update the member
    data = {
        "members": [{"type": "group", "id": str(group.name)}],
        "visible": True,
    }
    member_service.update(owner.identity, community._record.id, data)


@pytest.mark.parametrize(
    "actor,role",
    [
        ("owner", "owner"),
        ("owner", "manager"),
        ("owner", "curator"),
        ("owner", "reader"),
        ("manager", "manager"),
        ("manager", "curator"),
        ("manager", "reader"),
    ],
)
def test_update_hidden_visibility_allowed(
    member_service, community, members, actor, role, new_user, db
):
    """Only members themselves can set public visibility."""
    # Add a new user with role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
        "visible": True,
    }
    member_service.add(system_identity, community._record.id, data)
    # Update the member with hidden visibility.
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "visible": False,
    }
    member_service.update(members[actor].identity, community._record.id, data)


@pytest.mark.parametrize(
    "actor,initial_role,new_role",
    [
        ("owner", "owner", "reader"),
        ("owner", "manager", "reader"),
        ("owner", "curator", "manager"),
        ("owner", "reader", "curator"),
        ("manager", "manager", "curator"),
        ("manager", "curator", "manager"),
        ("manager", "reader", "curator"),
    ],
)
def test_update_role_allowed(
    member_service, community, members, actor, initial_role, new_role, new_user, db
):
    """Owners can change role of all, managers all but owners."""
    # Add a new user with role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": initial_role,
    }
    member_service.add(system_identity, community._record.id, data)
    # Update the member with new role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": new_role,
    }
    member_service.update(members[actor].identity, community._record.id, data)


@pytest.mark.parametrize(
    "actor,initial_role,new_role",
    [
        ("manager", "owner", "reader"),
        ("curator", "owner", "reader"),
        ("curator", "manager", "curator"),
        ("curator", "curator", "manager"),
        ("curator", "reader", "owner"),
        ("reader", "owner", "owner"),
        ("reader", "manager", "manager"),
        ("reader", "curator", "curator"),
        ("reader", "reader", "manager"),
    ],
)
def test_update_role_denied(
    member_service, community, members, actor, initial_role, new_role, new_user, db
):
    """Managers cannot change owner roles, curators/readers cannot change."""
    # Add a new user with role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": initial_role,
    }
    member_service.add(system_identity, community._record.id, data)
    # Update the member with new role
    data["role"] = new_role
    pytest.raises(
        PermissionDeniedError,
        member_service.update,
        members[actor].identity,
        community._record.id,
        data,
    )


@pytest.mark.parametrize(
    "actor,initial_role,new_role",
    [
        ("owner", "owner", "reader"),
        ("owner", "manager", "reader"),
        ("owner", "curator", "manager"),
        ("owner", "reader", "curator"),
        ("manager", "manager", "curator"),
        ("manager", "curator", "manager"),
        ("manager", "reader", "curator"),
    ],
)
def test_update_invitation_role_allowed(
    member_service, community, members, actor, initial_role, new_role, new_user, db
):
    """Owners can change role of all, managers all but owners."""
    # Invite a new user with role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": initial_role,
    }
    member_service.invite(members[actor].identity, community._record.id, data)

    # Update the invitation with new role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": new_role,
    }
    member_service.update(members[actor].identity, community._record.id, data)


@pytest.mark.parametrize(
    "actor,initial_role,new_role",
    [
        ("manager", "owner", "reader"),
        ("curator", "owner", "reader"),
        ("curator", "manager", "curator"),
        ("curator", "curator", "manager"),
        ("curator", "reader", "owner"),
        ("reader", "owner", "owner"),
        ("reader", "manager", "manager"),
        ("reader", "curator", "curator"),
        ("reader", "reader", "manager"),
    ],
)
def test_update_invitation_role_denied(
    member_service, community, members, actor, initial_role, new_role, new_user, db
):
    """Managers cannot change owner roles, curators/readers cannot change."""
    # Invite a new user with role
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": initial_role,
    }
    member_service.invite(members["owner"].identity, community._record.id, data)

    # Update the invitation with new role
    data["role"] = new_role
    pytest.raises(
        PermissionDeniedError,
        member_service.update,
        members[actor].identity,
        community._record.id,
        data,
    )


@pytest.mark.parametrize("action", ["decline", "cancel", "expire"])
def test_update_declined_invitation(
    member_service,
    requests_service,
    community,
    owner,
    invite_user,
    invite_request_id,
    db,
    action,
):
    """A declined/cancelled invitation cannot be updated."""
    requests_service.execute_action(
        system_identity, invite_request_id, action
    ).to_dict()

    # Update the invitation with new role
    data = {
        "members": [{"type": "user", "id": str(invite_user.id)}],
        "role": "reader",
    }
    assert pytest.raises(
        InvalidMemberError,
        member_service.update,
        owner.identity,
        community._record.id,
        data,
    )


def test_update_role_must_have_owner(member_service, community, owner, group, db):
    """There must always be at least one owner."""
    # Add an owner group
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": "owner",
    }
    member_service.add(system_identity, community._record.id, data)

    # Update the both owners with manager role using system_identity
    data = {
        "members": [
            {"type": "group", "id": group.name},
            {"type": "user", "id": str(owner.id)},
        ],
        "role": "manager",
    }
    pytest.raises(
        ValidationError,
        member_service.update,
        system_identity,
        community._record.id,
        data,
    )


def test_update_invalid_data(member_service, community, group):
    # No role or visibility
    data = {
        "members": [{"type": "group", "id": group.name}],
    }
    pytest.raises(
        ValidationError,
        member_service.update,
        system_identity,
        community._record.id,
        data,
    )
    # Invalid type
    data = {"members": [{"type": "email", "id": group.name}], "role": "owner"}
    pytest.raises(
        InvalidMemberError,
        member_service.update,
        system_identity,
        community._record.id,
        data,
    )
    data = {"members": [{"type": "invalid", "id": group.name}], "role": "owner"}
    pytest.raises(
        ValidationError,
        member_service.update,
        system_identity,
        community._record.id,
        data,
    )
    # No members
    data = {"members": [], "role": "owner"}
    pytest.raises(
        ValidationError,
        member_service.update,
        system_identity,
        community._record.id,
        data,
    )
    # Missing member
    data = {"members": [{"type": "group", "id": "invalid"}], "role": "owner"}
    pytest.raises(
        InvalidMemberError,
        member_service.update,
        system_identity,
        community._record.id,
        data,
    )


#
# Change notifications
#
def test_relation_update_propagation(
    app, db, clean_index, public_reader, community, member_service
):
    comm_uuid = community._record.id
    # there is no .read() implementation
    comm_members = member_service.search_public(system_identity, comm_uuid)
    assert comm_members.total == 1

    member = list(comm_members.hits)[0]
    assert member.get("member").get("name") == "New User"

    # update user
    user_id = member["member"]["id"]
    user = current_datastore.get_user(user_id)
    user.user_profile = {"full_name": "Update test", "affiliations": "CERN"}
    current_datastore.commit()

    # check community has been updated
    assert member_service.indexer.process_bulk_queue() == (1, 0)
    Member.index.refresh()
    comm_members = member_service.search_public(system_identity, comm_uuid)
    assert comm_members.total == 1

    member = list(comm_members.hits)[0]
    assert member.get("member").get("name") == "Update test"
