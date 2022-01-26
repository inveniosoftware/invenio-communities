# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

import pytest
from invenio_requests.records import Request

from invenio_communities.invitations import AlreadyInvitedError
from invenio_communities.members import AlreadyMemberError, Member
from invenio_records_resources.services.errors import PermissionDeniedError


def test_cant_invite(
        community_service, community_creation_input_data, create_user_identity,
        generate_invitation_input_data, make_member_identity):
    owner_identity = create_user_identity("owner@example.com")
    # Creating a community also creates an owner membership
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    Member.index.refresh()
    owner_identity = make_member_identity(owner_identity, community, "owner")
    user_identity1 = create_user_identity("user1@example.com")
    user_identity2 = create_user_identity("user2@example.com")

    # if already invited
    data = generate_invitation_input_data(
        community.id, {"user": user_identity1.id}, "reader"
    )
    invitation = community_service.invitations.create(owner_identity, data)
    Request.index.refresh()

    with pytest.raises(AlreadyInvitedError):
        community_service.invitations.create(owner_identity, data)

    # if already member
    membership = community_service.members.create(
        owner_identity,
        data={
            "community": str(community.id),
            "user": user_identity2.id,
            "role": "reader"
        }
    )._record
    Member.index.refresh()
    data = generate_invitation_input_data(
        community.id, {"user": user_identity2.id}, "reader"
    )

    with pytest.raises(AlreadyMemberError):
        community_service.invitations.create(owner_identity, data)


def test_only_owner_can_invite_other_owner(
        community_creation_input_data, community_service,
        create_community_identity, create_user_identity,
        generate_invitation_input_data, make_member_identity):
    owner_identity = create_user_identity("owner@example.com")
    # Creating a community also creates an owner membership
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    Member.index.refresh()
    owner_identity = make_member_identity(owner_identity, community, "owner")

    # Owner can
    user_identity1 = create_user_identity("user1@example.com")
    data = generate_invitation_input_data(
        community.id, {"user": user_identity1.id}, "owner"
    )

    # No exception raised
    community_service.invitations.create(owner_identity, data)

    # Manager can't
    manager_identity = create_community_identity(community, "manager")
    user_identity2 = create_user_identity("user2@example.com")
    data = generate_invitation_input_data(
        community.id, {"user": user_identity2.id}, "owner"
    )

    with pytest.raises(PermissionDeniedError):
        community_service.invitations.create(manager_identity, data)


def test_only_owner_can_update_invitation_role_to_owner(
        community_creation_input_data, community_service,
        create_community_identity, create_user_identity,
        generate_invitation_input_data, make_member_identity):
    owner_identity = create_user_identity("owner@example.com")
    # Creating a community also creates an owner membership
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    Member.index.refresh()
    owner_identity = make_member_identity(owner_identity, community, "owner")

    # Owner can
    user_identity1 = create_user_identity("user1@example.com")
    data = generate_invitation_input_data(
        community.id, {"user": str(user_identity1.id)}, "reader"
    )
    invitation = community_service.invitations.create(owner_identity, data)
    data["payload"]["role"] = "owner"

    # No exception raised
    community_service.invitations.update(owner_identity, invitation.id, data)

    # Manager can't
    manager_identity = create_community_identity(community, "manager")
    user_identity2 = create_user_identity("user2@example.com")
    data = generate_invitation_input_data(
        community.id, {"user": str(user_identity2.id)}, "reader"
    )
    invitation = community_service.invitations.create(manager_identity, data)
    data["payload"]["role"] = "owner"

    with pytest.raises(PermissionDeniedError):
        community_service.invitations.update(
            manager_identity, invitation.id, data
        )
