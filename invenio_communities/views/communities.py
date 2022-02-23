# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Routes for community-related pages provided by Invenio-Communities."""

from flask import current_app, render_template
from flask_login import login_required

from .decorators import pass_community, pass_community_logo, \
    require_community_owner

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
                visibilty=[
                    {
                        'text': 'Public',
                        'value': 'public',
                        'icon': 'group',
                        'helpText': 'Your community is publicly accessible ' \
                                    'and shows up in search results.'
                    },
                    {
                        'text': 'Restricted',
                        'value': 'restricted',
                        'icon': 'lock',
                        'helpText': 'Your community is restricted to users ' \
                                    'with access.'
                    }
                ]
            ),
            SITE_UI_URL=current_app.config["SITE_UI_URL"]
        ),
    )

@pass_community
@pass_community_logo
def communities_detail(community=None, logo=None, pid_value=None):
    """Community detail page."""
    return render_template(
        "invenio_communities/details/index.html",
        community=community.to_dict(), # TODO: use serializer
        logo=logo.to_dict() if logo else None,
        # TODO: inject this from a vocabulary in the community
        types={
            "organization": "Organization",
            "event": "Event",
            "topic": "Topic",
            "project": "Project"
        },
        # Pass permissions so we can disable partially UI components
        # e.g Settings tab
        permissions=community.has_permissions_to(['update']),
        active_menu_tab="search"
    )

@pass_community
@pass_community_logo
@require_community_owner
def communities_settings(community=None, logo=None, pid_value=None):
    """Community settings/profile page."""
    return render_template(
        "invenio_communities/details/settings/profile.html",
        community=community.to_dict(), # TODO: use serializer,
        logo=logo.to_dict() if logo else None,
        # TODO: inject this from a vocabulary in the community
        types={
            "organization": "Organization",
            "event": "Event",
            "topic": "Topic",
            "project": "Project"
        },
        # Pass permissions so we can disable partially UI components
        # e.g Settings tab
        permissions=community.has_permissions_to(['update']),
        active_menu_tab="settings"
    )

@require_community_owner
@pass_community
@pass_community_logo
def communities_settings_privileges(community=None, logo=None, pid_value=None):
    """Community settings/privileges page."""
    return render_template(
        "invenio_communities/details/settings/privileges.html",
        community=community.to_dict(), # TODO: use serializer,
        form_config=dict(
            access=dict(
                visibilty=[
                    {
                        'text': 'Public',
                        'value': 'public',
                        'icon': 'group',
                        'helpText': 'Your community is publicly accessible ' \
                                    'and shows up in search results.'
                    },
                    {
                        'text': 'Restricted',
                        'value': 'restricted',
                        'icon': 'lock',
                        'helpText': 'Your community is restricted to users ' \
                                    'with access.'
                    }
                ]
            ),
        ),
        # TODO: inject this from a vocabulary in the community
        types={
            "organization": "Organization",
            "event": "Event",
            "topic": "Topic",
            "project": "Project"
        },
        # Pass permissions so we can disable partially UI components
        # e.g Settings tab
        permissions=community.has_permissions_to(['update']),
        active_menu_tab="settings",
        logo=logo.to_dict() if logo else None
    )
