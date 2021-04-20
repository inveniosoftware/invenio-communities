# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Routes for community-related pages provided by Invenio-Communities."""

from flask import current_app, render_template
from flask_login import login_required

from .decorators import pass_community

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
    )

@pass_community
def communities_detail(community=None, pid_value=None):
    """Community detail page."""
    return render_template(
        "invenio_communities/details/index.html",
        community=community.to_dict(), # TODO: use serializer
        active_menu_tab="search"
    )

@pass_community
def communities_settings(community=None, pid_value=None):
    """Community settings page."""
    return render_template(
        "invenio_communities/details/settings/index.html",
        community=community.to_dict(), # TODO: use serializer,
        form_config=dict(
            domains=current_app.config["COMMUNITIES_DOMAINS"]
        ),
        active_menu_tab="settings"
    )
