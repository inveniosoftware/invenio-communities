# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

import pytest

from invenio_communities.invitations import InvitationPermissionPolicy


@pytest.fixture(scope="module")
def policy():
    """Permission policy under test."""
    return InvitationPermissionPolicy


def test_only_owner_manager_can_invite(
        anyuser_identity, community_service, create_user_identity,
        community_creation_input_data, make_member_identity,
        create_community_identity, policy):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    manager_identity = create_community_identity(community, "manager")
    member_identity = create_community_identity(community, "member")

    assert (
        policy(action='create', record=community)
        .allows(owner_identity)
    )
    assert (
        policy(action='create', record=community)
        .allows(manager_identity)
    )
    assert not (
        policy(action='create', record=community)
        .allows(member_identity)
    )
    assert not (
        policy(action='create', record=community)
        .allows(anyuser_identity)
    )


def test_can_read_invitation(
        anyuser_identity, community_service, create_user_identity,
        community_creation_input_data, generate_invitation_input_data,
        make_member_identity, create_community_identity, policy):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    manager_identity = create_community_identity(community, "manager")
    user_identity = create_user_identity("user@example.com")
    data = generate_invitation_input_data(
        community.id, {"user": user_identity.id}
    )
    invitation = community_service.invitations.create(
        owner_identity, data
    )._obj
    member_identity = create_community_identity(community, "member")

    assert (
        policy(action='read', request=invitation)
        .allows(owner_identity)
    )
    assert (
        policy(action='read', request=invitation)
        .allows(manager_identity)
    )
    assert (
        policy(action='read', request=invitation)
        .allows(user_identity)
    )
    assert not (
        policy(action='read', request=invitation)
        .allows(member_identity)
    )
    assert not (
        policy(action='read', request=invitation)
        .allows(anyuser_identity)
    )


def test_only_owner_manager_can_update_invitation(
        anyuser_identity, community_service, create_user_identity,
        community_creation_input_data, generate_invitation_input_data,
        make_member_identity, create_community_identity, policy):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    manager_identity = create_community_identity(community, "manager")
    user_identity = create_user_identity("user@example.com")
    data = generate_invitation_input_data(
        community.id, {"user": user_identity.id}
    )
    invitation = community_service.invitations.create(
        owner_identity, data
    )._obj
    member_identity = create_community_identity(community, "member")

    assert (
        policy(action='update', request=invitation)
        .allows(owner_identity)
    )
    assert (
        policy(action='update', request=invitation)
        .allows(manager_identity)
    )
    assert not (
        policy(action='update', request=invitation)
        .allows(member_identity)
    )
    assert not (
        policy(action='update', request=invitation)
        .allows(anyuser_identity)
    )


def test_only_owner_manager_can_cancel_invitation(
        anyuser_identity, community_service, create_user_identity,
        community_creation_input_data, generate_invitation_input_data,
        make_member_identity, create_community_identity, policy):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    manager_identity = create_community_identity(community, "manager")
    user_identity = create_user_identity("user@example.com")
    data = generate_invitation_input_data(
        community.id, {"user": user_identity.id}
    )
    invitation = community_service.invitations.create(
        owner_identity, data
    )._obj
    member_identity = create_community_identity(community, "member")

    assert (
        policy(action='action_cancel', request=invitation)
        .allows(owner_identity)
    )
    assert (
        policy(action='action_cancel', request=invitation)
        .allows(manager_identity)
    )
    assert not (
        policy(action='action_cancel', request=invitation)
        .allows(member_identity)
    )
    assert not (
        policy(action='action_cancel', request=invitation)
        .allows(anyuser_identity)
    )


def test_only_invitee_can_accept_decline_invitation(
        anyuser_identity, community_service, create_user_identity,
        community_creation_input_data, generate_invitation_input_data,
        make_member_identity, create_community_identity, policy):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    manager_identity = create_community_identity(community, "manager")
    user_identity = create_user_identity("user@example.com")
    data = generate_invitation_input_data(
        community.id, {"user": user_identity.id}
    )
    invitation = community_service.invitations.create(
        owner_identity, data
    )._obj
    member_identity = create_community_identity(community, "member")
    cant_identity = [
        owner_identity,
        manager_identity,
        member_identity,
        anyuser_identity
    ]

    for action in ["action_accept", "action_decline"]:
        for identity in cant_identity:
            assert not (
                policy(action=action, request=invitation)
                .allows(identity)
            )

    for action in ["action_accept", "action_decline"]:
        assert (
            policy(action=action, request=invitation)
            .allows(user_identity)
        )
