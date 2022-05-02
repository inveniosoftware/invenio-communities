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

from .decorators import pass_community, pass_community_logo


#
# Views
#

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
            access=dict(
                visibility=[
                    {
                        'text': 'Public',
                        'value': 'public',
                        'icon': 'group',
                        'helpText': _('Your community is publicly accessible'
                                      ' and shows up in search results.')
                    },
                    {
                        'text': 'Restricted',
                        'value': 'restricted',
                        'icon': 'lock',
                        'helpText': _('Your community is restricted to users'
                                      ' with access.')
                    }
                ]
            ),
            SITE_UI_URL=current_app.config["SITE_UI_URL"]
        ),
    )


@pass_community
@pass_community_logo
def communities_settings(community=None, logo=None, pid_value=None):
    """Community settings/profile page."""
    permissions = community.has_permissions_to(
        ['update', 'read', 'search_requests', 'search_invites']
    )
    if not permissions['can_update']:
        raise PermissionDeniedError()
    return render_template(
        "invenio_communities/details/settings/profile.html",
        community=community.to_dict(),  # TODO: use serializer,
        logo=logo.to_dict() if logo else None,
        # TODO: inject this from a vocabulary in the community
        types={
            "organization": _("Organization"),
            "event": _("Event"),
            "topic": _("Topic"),
            "project": _("Project")
        },
        # Pass permissions so we can disable partially UI components
        # e.g Settings tab
        permissions=permissions,
        active_menu_tab="settings"
    )


@pass_community
@pass_community_logo
def communities_requests(community=None, logo=None, pid_value=None):
    """Community requests page."""
    permissions = community.has_permissions_to(
        ['update', 'read', 'search_requests', 'search_invites']
    )
    if not permissions['can_search_requests']:
        raise PermissionDeniedError()
    return render_template(
        "invenio_communities/details/requests/index.html",
        community=community.to_dict(),  # TODO: use serializer,
        logo=logo.to_dict() if logo else None,
        # TODO: inject this from a vocabulary in the community
        types={
            "organization": _("Organization"),
            "event": _("Event"),
            "topic": _("Topic"),
            "project": _("Project")
        },
        # Pass permissions so we can disable partially UI components
        # e.g Settings tab
        permissions=permissions,
    )


@pass_community
@pass_community_logo
def communities_settings_privileges(community=None, logo=None, pid_value=None):
    """Community settings/privileges page."""
    permissions = community.has_permissions_to(
        ['update', 'read', 'search_requests', 'search_invites']
    )
    if not permissions['can_update']:
        raise PermissionDeniedError()
    return render_template(
        "invenio_communities/details/settings/privileges.html",
        community=community.to_dict(),  # TODO: use serializer,
        form_config=dict(
            access=dict(
                visibility=[
                    {
                        'text': 'Public',
                        'value': 'public',
                        'icon': 'group',
                        'helpText': _('Your community is publicly accessible'
                                      ' and shows up in search results.')
                    },
                    {
                        'text': 'Restricted',
                        'value': 'restricted',
                        'icon': 'lock',
                        'helpText': _('Your community is restricted to users'
                                      ' with access.')
                    }
                ]
            ),
        ),
        # TODO: inject this from a vocabulary in the community
        types={
            "organization": _("Organization"),
            "event": _("Event"),
            "topic": _("Topic"),
            "project": _("Project")
        },
        # Pass permissions so we can disable partially UI components
        # e.g Settings tab
        permissions=permissions,
        logo=logo.to_dict() if logo else None
    )


@pass_community
def members(community=None, pid_value=None, endpoint=None):
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
            "invite_owners"
        ]
    )
    if not permissions['can_read']:
        raise PermissionDeniedError()
    return render_template(
        "invenio_communities/details/members/members.html",
        community=community.to_dict(),
        types={
            "organization": _("Organization"),
            "event": _("Event"),
            "topic": _("Topic"),
            "project": _("Project")
        },
        permissions=permissions,
    )


@pass_community
def invitations(community=None, pid_value=None):
    """Community invitations page."""
    permissions = community.has_permissions_to(
        ['update', 'read', 'search_requests', 'search_invites',
         'invite_owners']
    )
    if not permissions['can_search_invites']:
        raise PermissionDeniedError()
    return render_template(
        "invenio_communities/details/members/invitations.html",
        community=community.to_dict(),
        types={
            "organization": _("Organization"),
            "event": _("Event"),
            "topic": _("Topic"),
            "project": _("Project")
        },
        permissions=permissions,
    )
