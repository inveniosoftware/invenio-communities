# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from collections import namedtuple
from functools import partial

from flask import g
from flask_principal import Identity, RoleNeed
from invenio_access.permissions import system_identity

from invenio_communities.communities.resources.serializer import (
    UICommunityJSONSerializer,
)
from invenio_communities.permissions import CommunityPermissionPolicy


def test_ui_serializer(app, community, users, any_user):
    owner = users["owner"]
    reader = users["reader"]
    closed_review_comm = community.to_dict()
    closed_review_comm["access"]["review_policy"] = "closed"
    closed_review_expected_data = {
        "permissions": {
            "can_include_directly": False,
            "can_update": True,
            "can_submit_record": True,
        }
    }

    # set current user to owner
    g.identity = owner.identity

    serialized_record = UICommunityJSONSerializer().dump_obj(closed_review_comm)
    assert (
        serialized_record["ui"]["permissions"]
        == closed_review_expected_data["permissions"]
    )

    open_review_comm = community.to_dict()
    open_review_comm["access"]["review_policy"] = "open"
    open_review_expected_data = {
        "permissions": {
            "can_include_directly": True,
            "can_update": True,
            "can_submit_record": True,
        }
    }

    serialized_record = UICommunityJSONSerializer().dump_obj(open_review_comm)
    assert (
        serialized_record["ui"]["permissions"]
        == open_review_expected_data["permissions"]
    )

    # set user to community reader
    g.identity = reader.identity
    require_review_expected_data = {
        "permissions": {
            "can_include_directly": False,
            "can_update": False,
            "can_submit_record": True,
        }
    }

    serialized_record = UICommunityJSONSerializer().dump_obj(open_review_comm)
    assert (
        serialized_record["ui"]["permissions"]
        == require_review_expected_data["permissions"]
    )

    # set user to any user
    g.identity = any_user.identity
    serialized_record = UICommunityJSONSerializer().dump_obj(open_review_comm)
    assert (
        serialized_record["ui"]["permissions"]
        == require_review_expected_data["permissions"]
    )


def test_can_include_directly_closed(
    app,
    db,
    community,
    anon_identity,
    any_user,
    superuser_identity,
    owner,
    community_service,
):
    """Test 'include_directly' permission with 'closed' review policy."""
    # Set the community's review policy to 'closed'
    community_data = community_service.read(system_identity, community.id).data
    community_data["access"]["review_policy"] = "closed"
    community_service.update(system_identity, community.id, community_data)
    community_record = community_service.read(system_identity, community.id)

    # Identities
    anonymous_identity = anon_identity
    authenticated_identity = any_user.identity
    owner_identity = owner.identity
    superuser_id = superuser_identity
    system_process_identity = system_identity

    # Community Creator
    community_creator_identity = Identity(any_user.id)
    community_creator_identity.provides.update(authenticated_identity.provides)
    community_creator_identity.provides.add(RoleNeed("community-creator"))

    # Community Member (Owner)
    member_identity = Identity(owner.id)
    member_identity.provides.update(owner_identity.provides)
    # Assume owner is a member

    _Need = namedtuple("Need", ["method", "value", "role"])
    CommunityRoleNeed = partial(_Need, "community")
    community_id = str(community.id)
    member_identity.provides.add(CommunityRoleNeed(community_id, "member"))

    # Community Curator
    curator_identity = Identity(any_user.id)
    curator_identity.provides.update(authenticated_identity.provides)
    curator_identity.provides.add(CommunityRoleNeed(community_id, "curator"))

    # Set RDM_COMMUNITY_REQUIRED_TO_PUBLISH to True
    app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = True

    policy = CommunityPermissionPolicy

    # Assertions: No one can include directly
    identities = [
        anonymous_identity,
        authenticated_identity,
        community_creator_identity,
        member_identity,
        curator_identity,
        owner_identity,
        superuser_id,
        system_process_identity,
    ]

    for identity in identities:
        assert not policy(action="include_directly", record=community_record).allows(
            identity
        )

    app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = False

    # Assertions remain the same: No one can include directly
    for identity in identities:
        assert not policy(action="include_directly", record=community_record).allows(
            identity
        )


def test_can_include_directly_open(
    app,
    db,
    community,
    anon_identity,
    any_user,
    superuser_identity,
    owner,
    community_service,
):
    """Test 'include_directly' permission with 'open' review policy."""
    # Set the community's review policy to 'open'
    community_data = community_service.read(system_identity, community.id).data
    community_data["access"]["review_policy"] = "open"
    community_service.update(system_identity, community.id, community_data)
    community_record = community_service.read(system_identity, community.id)

    # Identities
    anonymous_identity = anon_identity
    authenticated_identity = any_user.identity
    owner_identity = owner.identity
    system_process_identity = system_identity

    # Create identities with roles
    from flask_principal import Identity, RoleNeed

    # Community Creator
    community_creator_identity = Identity(any_user.id)
    community_creator_identity.provides.update(authenticated_identity.provides)
    community_creator_identity.provides.add(RoleNeed("community-creator"))

    # Community Curator
    from collections import namedtuple
    from functools import partial

    _Need = namedtuple("Need", ["method", "value", "role"])
    CommunityRoleNeed = partial(_Need, "community")
    community_id = str(community.id)
    curator_identity = Identity(any_user.id)
    curator_identity.provides.update(authenticated_identity.provides)
    curator_identity.provides.add(CommunityRoleNeed(community_id, "curator"))

    # Set RDM_COMMUNITY_REQUIRED_TO_PUBLISH to False
    app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = False

    policy = CommunityPermissionPolicy

    # Assertions when RDM_COMMUNITY_REQUIRED_TO_PUBLISH is False
    # Only community curators can include directly
    # Superuser should not be allowed
    assert not policy(action="include_directly", record=community_record).allows(
        anonymous_identity
    )
    assert not policy(action="include_directly", record=community_record).allows(
        authenticated_identity
    )
    assert not policy(action="include_directly", record=community_record).allows(
        community_creator_identity
    )

    # Community curator can include directly
    assert policy(action="include_directly", record=community_record).allows(
        curator_identity
    )


def test_can_include_directly_members(
    app,
    db,
    community,
    anon_identity,
    any_user,
    superuser_identity,
    owner,
    community_service,
):
    """Test 'include_directly' permission with 'members' review policy."""
    # Set the community's review policy to 'members'
    community_data = community_service.read(system_identity, community.id).data
    community_data["access"]["review_policy"] = "members"
    community_service.update(system_identity, community.id, community_data)
    community_record = community_service.read(system_identity, community.id)

    # Identities
    anonymous_identity = anon_identity
    authenticated_identity = any_user.identity
    owner_identity = owner.identity
    superuser_id = superuser_identity
    system_process_identity = system_identity

    # Create identities with roles
    from flask_principal import Identity, RoleNeed

    # Community Creator
    community_creator_identity = Identity(any_user.id)
    community_creator_identity.provides.update(authenticated_identity.provides)
    community_creator_identity.provides.add(RoleNeed("community-creator"))

    # Community Member
    member_identity = Identity(any_user.id)
    member_identity.provides.update(authenticated_identity.provides)
    from collections import namedtuple
    from functools import partial

    _Need = namedtuple("Need", ["method", "value", "role"])
    CommunityRoleNeed = partial(_Need, "community")
    community_id = str(community.id)
    member_identity.provides.add(CommunityRoleNeed(community_id, "member"))

    # Assume owner is a member
    owner_member_identity = Identity(owner.id)
    owner_member_identity.provides.update(owner_identity.provides)
    owner_member_identity.provides.add(CommunityRoleNeed(community_id, "member"))

    # Set RDM_COMMUNITY_REQUIRED_TO_PUBLISH to True
    app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = True

    policy = CommunityPermissionPolicy

    # Assertions when RDM_COMMUNITY_REQUIRED_TO_PUBLISH is True
    identities = [
        anonymous_identity,
        authenticated_identity,
        community_creator_identity,
        member_identity,
    ]

    # All users are denied
    for identity in identities:
        assert not policy(action="include_directly", record=community_record).allows(
            identity
        )

    # Set RDM_COMMUNITY_REQUIRED_TO_PUBLISH to False
    app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = False

    # Assertions when RDM_COMMUNITY_REQUIRED_TO_PUBLISH is False
    # Only community members can include directly
    for identity in [
        anonymous_identity,
        authenticated_identity,
        community_creator_identity,
        system_process_identity,
    ]:
        assert not policy(action="include_directly", record=community_record).allows(
            identity
        )
