# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community views."""

from invenio_communities.views.communities import _filter_roles


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
