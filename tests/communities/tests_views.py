# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2023 KTH Royal Institute of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community views."""

from flask import g
from invenio_records_permissions.generators import SystemProcess

from invenio_communities.permissions import CommunityPermissionPolicy
from invenio_communities.views.communities import _filter_roles
from invenio_communities.views.ui import _show_create_community_link


def _test_filter_roles(app, members, action, member_types, community_id):
    """Test _filter_roles func."""
    for role in app.config["COMMUNITIES_ROLES"]:
        role_name = role["name"]
        member = members[role_name]

        roles = _filter_roles(
            action, member_types, community_id, identity=member.identity
        )
        filtered = {role["name"] for role in roles}
        assert filtered == set(role.get("can_manage_roles", []))


def test_filter_roles_when_updating_roles(
    app, db, community_service, community, members
):
    """Test selectable roles when updating existing members' roles."""
    _test_filter_roles(
        app,
        members,
        "members_update",
        {"user", "group"},
        community.id,
    )


def test_filter_roles_when_inviting_members(
    app, db, community_service, community, members
):
    """Test selectable roles when inviting new members."""
    _test_filter_roles(
        app,
        members,
        "members_invite",
        {"user"},
        community.id,
    )


def test_filter_roles_when_adding_groups(
    app, db, community_service, community, members
):
    """Test selectable roles when adding new groups."""
    _test_filter_roles(
        app,
        members,
        "members_add",
        {"group"},
        community.id,
    )


def test_show_create_community_link(app, users, superuser_identity):
    """Test the _can_create_community function under different config settings."""
    test_users = ["reader", "curator", "manager", "owner"]
    ALWAYS_SHOW_CREATE_LINK = "COMMUNITIES_ALWAYS_SHOW_CREATE_LINK"

    # Test default config allows community creation
    assert app.config.get(ALWAYS_SHOW_CREATE_LINK) == False
    assert _show_create_community_link() == True

    # Test with config set to True
    app.config[ALWAYS_SHOW_CREATE_LINK] = True
    assert app.config.get(ALWAYS_SHOW_CREATE_LINK) == True
    assert _show_create_community_link() == True

    # Test with different user identities
    for user in test_users:
        g.identity = users[user].identity
        assert _show_create_community_link() == True

    # Test with community creation disabled
    CommunityPermissionPolicy.can_create = [SystemProcess()]
    for user in test_users:
        g.identity = users[user].identity
        assert _show_create_community_link() == False

    # Test superuser
    g.identity = superuser_identity
    assert _show_create_community_link() == True
