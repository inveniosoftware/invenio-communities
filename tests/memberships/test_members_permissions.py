# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from copy import deepcopy

from invenio_communities.permissions import CommunityPermissionPolicy
from invenio_communities.members import Member


def test_anyone_can_search_members_of_public_community(
        anyuser_identity, community_service, community_owner_identity,
        community_creation_input_data):
    # public community
    community = community_service.create(
        community_owner_identity,
        community_creation_input_data
    )._record
    policy = CommunityPermissionPolicy

    assert (
        policy(action='search_members', record=community)
        .allows(anyuser_identity)
    )


def test_only_a_member_can_search_members_of_restricted_community(
        anyuser_identity, community_service, community_owner_identity,
        community_creation_input_data, make_member_identity):
    # private community
    data = deepcopy(community_creation_input_data)
    data["access"]["visibility"] = "restricted"
    community = community_service.create(
        community_owner_identity,
        data
    )._record
    policy = CommunityPermissionPolicy

    # Any user can't
    assert not (
        policy(action='search_members', record=community)
        .allows(anyuser_identity)
    )

    # Reader, Curator, Manager, Owner can
    member_identity = make_member_identity(anyuser_identity, community)
    assert (
        policy(action='search_members', record=community)
        .allows(member_identity)
    )


def test_can_delete_member(
        create_user_identity, community_service, community_creation_input_data,
        make_member_identity):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    owner_membership = community_service.members.get_member(
        community.id, owner_identity.id
    )
    policy = CommunityPermissionPolicy

    # Member can leave
    member1_identity = create_user_identity("member1@example.com")
    member1_identity = make_member_identity(
        member1_identity, community, "reader")
    membership = Member.create(
        {},
        community_id=community.id,
        user_id=member1_identity.id,
        role="reader"
    )

    assert (
        policy(action="delete_member", record=membership)
        .allows(member1_identity)
    )

    # Owner and manager can remove other member
    assert (
        policy(action="delete_member", record=membership)
        .allows(owner_identity)
    )

    manager_identity = create_user_identity("manager@example.com")
    manager_identity = make_member_identity(
        manager_identity, community, "manager"
    )

    assert (
        policy(action="delete_member", record=membership)
        .allows(manager_identity)
    )

    # Manager can't remove owner
    assert not (
        policy(action="delete_member", record=owner_membership)
        .allows(manager_identity)
    )

    # Non-member and member can't remove other member
    non_member_identity = create_user_identity("user@example.com")

    assert not (
        policy(action="delete_member", record=membership)
        .allows(non_member_identity)
    )

    member2_identity = make_member_identity(
        non_member_identity, community, "reader")

    assert not (
        policy(action="delete_member", record=membership)
        .allows(member2_identity)
    )


def test_can_update_member(
        create_user_identity, community_service, community_creation_input_data,
        make_member_identity):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    owner_membership = community_service.members.get_member(
        community.id, owner_identity.id
    )

    policy = CommunityPermissionPolicy

    # Member can update self
    member1_identity = create_user_identity("member1@example.com")
    member1_identity = make_member_identity(
        member1_identity, community, "reader")
    membership = Member.create(
        {},
        community_id=community.id,
        user_id=member1_identity.id,
        role="reader"
    )

    assert (
        policy(action="update_member", record=membership)
        .allows(member1_identity)
    )

    # Owner and manager can update other member
    assert (
        policy(action="update_member", record=membership)
        .allows(owner_identity)
    )

    manager_identity = create_user_identity("manager@example.com")
    manager_identity = make_member_identity(
        manager_identity, community, "manager"
    )

    assert (
        policy(action="update_member", record=membership)
        .allows(manager_identity)
    )

    # Manager can't update owner
    assert not (
        policy(action="update_member", record=owner_membership)
        .allows(manager_identity)
    )

    # Non-member and member can't update other member
    non_member_identity = create_user_identity("user@example.com")

    assert not (
        policy(action="update_member", record=membership)
        .allows(non_member_identity)
    )

    member2_identity = make_member_identity(
        non_member_identity, community, "reader")

    assert not (
        policy(action="update_member", record=membership)
        .allows(member2_identity)
    )


def test_can_read_member_of_public_community(
        anyuser_identity, create_user_identity, community_service,
        make_member_identity, community_creation_input_data):
    owner_identity = create_user_identity("owner@example.com")
    # public community
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    member_identity = create_user_identity("member@example.com")
    member_identity = make_member_identity(
        member_identity, community, "reader")
    membership = Member.create(
        {},
        community_id=community.id,
        user_id=member_identity.id,
        role="reader"
    )
    policy = CommunityPermissionPolicy

    # Any user (even guests) can read member
    assert (
        policy(action='read_member', record=membership)
        .allows(anyuser_identity)
    )


def test_can_read_member_of_restricted_community(
        anyuser_identity, create_user_identity, community_service,
        make_member_identity, community_creation_input_data):
    owner_identity = create_user_identity("owner@example.com")
    # private community
    data = deepcopy(community_creation_input_data)
    data["access"]["visibility"] = "restricted"
    community = community_service.create(
        owner_identity,
        data
    )._record
    member_identity = create_user_identity("member@example.com")
    membership = Member.create(
        {},
        community_id=community.id,
        user_id=member_identity.id,
        role="reader"
    )
    member_identity = make_member_identity(member_identity, community)
    policy = CommunityPermissionPolicy

    # Any user can't
    assert not (
        policy(action='read_member', record=membership)
        .allows(anyuser_identity)
    )

    # Member can
    assert (
        policy(action='read_member', record=membership)
        .allows(member_identity)
    )


def test_can_create_member(
        create_user_identity, community_service, community_creation_input_data,
        make_member_identity):
    owner_identity = create_user_identity("owner@example.com")
    community = community_service.create(
        owner_identity,
        community_creation_input_data
    )._record
    owner_identity = make_member_identity(owner_identity, community, "owner")
    policy = CommunityPermissionPolicy


    # Owner can
    assert (
        policy(action="create_member", record=community)
        .allows(owner_identity)
    )

    # Manager can
    manager_identity = create_user_identity("manager@example.com")
    manager_identity = make_member_identity(
        manager_identity, community, "manager"
    )

    assert (
        policy(action="create_member", record=community)
        .allows(manager_identity)
    )

    # Member can't
    member_identity = create_user_identity("member@example.com")
    member_identity = make_member_identity(member_identity, community)

    assert not (
        policy(action="create_member", record=community)
        .allows(member_identity)
    )
