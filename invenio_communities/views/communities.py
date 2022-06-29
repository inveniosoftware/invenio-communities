# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Routes for community-related pages provided by Invenio-Communities."""

from flask import current_app, g, render_template
from flask_babelex import lazy_gettext as _
from flask_login import login_required
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_vocabularies.proxies import current_service as vocabulary_service

from invenio_communities.proxies import current_communities

from ..communities.resources.ui_schema import TypesSchema
from .decorators import pass_community

VISIBILITY_FIELDS = [
    {
        "text": "Public",
        "value": "public",
        "icon": "group",
        "helpText": _(
            "Your community is publicly accessible" " and shows up in search results."
        ),
    },
    {
        "text": "Restricted",
        "value": "restricted",
        "icon": "lock",
        "helpText": _("Your community is restricted to users" " with access."),
    },
]


def _filter_roles(action, member_types, community_id, identity=None):
    """Compute current identity roles for action, member type and community."""
    identity = identity or g.identity
    service_config = current_communities.service.config
    roles = []
    for role in current_app.config["COMMUNITIES_ROLES"]:
        permission = service_config.permission_policy_cls(
            action,
            community_id=community_id,
            role=role["name"],
            member_types=member_types,
        )
        if permission.allows(identity):
            roles.append(role)
    return roles


def _get_roles_can_update(community_id):
    """Get the full list of roles that current identity can update."""
    return _filter_roles("members_update", {"user", "group"}, community_id)


def _get_roles_can_invite(community_id):
    """Get the full list of roles that current identity can invite."""
    return dict(
        user=_filter_roles("members_invite", {"user"}, community_id),
        group=_filter_roles("members_add", {"group"}, community_id),
    )


def communities_frontpage():
    """Communities index page."""
    return render_template(
        "invenio_communities/frontpage.html",
    )


def communities_search():
    """Communities search page."""
    return render_template(
        "invenio_communities/search.html",
    )


@login_required
def communities_new():
    """Communities creation page."""
    return render_template(
        "invenio_communities/new.html",
        form_config=dict(
            access=dict(visibility=VISIBILITY_FIELDS),
            SITE_UI_URL=current_app.config["SITE_UI_URL"],
        ),
    )


@pass_community(serialize=True)
def communities_settings(pid_value, community, community_ui):
    """Community settings/profile page."""
    permissions = community.has_permissions_to(
        ["update", "read", "search_requests", "search_invites"]
    )
    if not permissions["can_update"]:
        raise PermissionDeniedError()

    _types = vocabulary_service.read_all(
        g.identity,
        fields=["id", "title"],
        type="communitytypes",
        max_records=10,
    )
    types_json = {
        "types": [{"id": i["id"], "title": i["title"]} for i in list(_types.hits)]
    }
    types_serialized = TypesSchema().dump(types_json)
    try:
        current_communities.service.read_logo(g.identity, pid_value)
        logo = True
    except FileNotFoundError:
        logo = False

    logo_size_limit = 10**6
    max_size = current_app.config["COMMUNITIES_LOGO_MAX_FILE_SIZE"]
    if type(max_size) is int and max_size > 0:
        logo_size_limit = max_size

    return render_template(
        "invenio_communities/details/settings/profile.html",
        community=community_ui,
        has_logo=True if logo else False,
        logo_quota=logo_size_limit,
        types=types_serialized["types"],
        permissions=permissions,  # hide/show UI components
        active_menu_tab="settings",
    )


@pass_community(serialize=True)
def communities_requests(pid_value, community, community_ui):
    """Community requests page."""
    permissions = community.has_permissions_to(
        ["update", "read", "search_requests", "search_invites"]
    )
    if not permissions["can_search_requests"]:
        raise PermissionDeniedError()

    return render_template(
        "invenio_communities/details/requests/index.html",
        community=community_ui,
        permissions=permissions,
    )


@pass_community(serialize=True)
def communities_settings_privileges(pid_value, community, community_ui):
    """Community settings/privileges page."""
    permissions = community.has_permissions_to(
        ["update", "read", "search_requests", "search_invites"]
    )
    if not permissions["can_update"]:
        raise PermissionDeniedError()

    return render_template(
        "invenio_communities/details/settings/privileges.html",
        community=community_ui,
        form_config=dict(
            access=dict(visibility=VISIBILITY_FIELDS),
        ),
        permissions=permissions,
    )


@pass_community(serialize=True)
def members(pid_value, community, community_ui):
    """Community members page."""
    permissions = community.has_permissions_to(
        [
            "update",
            "members_search",
            "members_search_public",
            "members_manage",
            "read",
            "search_requests",
            "search_invites",
            "invite_owners",
        ]
    )
    if not permissions["can_read"]:
        raise PermissionDeniedError()

    return render_template(
        "invenio_communities/details/members/members.html",
        community=community_ui,
        permissions=permissions,
        roles_can_update=_get_roles_can_update(community.id),
    )


@pass_community(serialize=True)
def invitations(pid_value, community, community_ui):
    """Community invitations page."""
    permissions = community.has_permissions_to(
        [
            "update",
            "read",
            "search_requests",
            "search_invites",
            "invite_owners",
        ]
    )
    if not permissions["can_search_invites"]:
        raise PermissionDeniedError()
    return render_template(
        "invenio_communities/details/members/invitations.html",
        community=community_ui,
        roles_can_invite=_get_roles_can_invite(community.id),
        permissions=permissions,
    )
