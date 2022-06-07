# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Communities UI views."""

from flask import Blueprint, current_app, render_template
from flask_babelex import lazy_gettext as _
from flask_login import current_user
from flask_menu import current_menu
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError

from ..searchapp import search_app_context
from .communities import (
    communities_frontpage,
    communities_new,
    communities_requests,
    communities_search,
    communities_settings,
    communities_settings_privileges,
    invitations,
    members,
)


#
# Error handlers
#
def not_found_error(error):
    """Handler for 'Not Found' errors."""
    return render_template(current_app.config["THEME_404_TEMPLATE"]), 404


def record_tombstone_error(error):
    """Tombstone page."""
    return render_template("invenio_communities/tombstone.html"), 410


def record_permission_denied_error(error):
    """Handle permission denier error on record views."""
    if not current_user.is_authenticated:
        # trigger the flask-login unauthorized handler
        return current_app.login_manager.unauthorized()
    return render_template(current_app.config["THEME_403_TEMPLATE"]), 403


#
# Registration
#
def create_ui_blueprint(app):
    """Register blueprint routes on app."""
    routes = app.config.get("COMMUNITIES_ROUTES")

    blueprint = Blueprint(
        "invenio_communities",
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # Communities URL rules
    blueprint.add_url_rule(
        routes["frontpage"],
        view_func=communities_frontpage,
    )

    blueprint.add_url_rule(
        routes["search"],
        view_func=communities_search,
    )

    blueprint.add_url_rule(
        routes["new"],
        view_func=communities_new,
    )

    # Settings tab routes
    blueprint.add_url_rule(
        routes["settings"],
        view_func=communities_settings,
    )

    blueprint.add_url_rule(
        routes["requests"],
        view_func=communities_requests,
    )

    blueprint.add_url_rule(
        routes["settings_privileges"],
        view_func=communities_settings_privileges,
    )

    blueprint.add_url_rule(routes["members"], view_func=members)

    blueprint.add_url_rule(routes["invitations"], view_func=invitations)

    @blueprint.before_app_first_request
    def register_menus():
        """Register community menu items."""
        item = current_menu.submenu("main.communities")
        item.register(
            "invenio_communities.communities_frontpage",
            "Communities",
            order=3,
        )

        item = current_menu.submenu("plus.community").register(
            "invenio_communities.communities_new",
            "New community",
            order=3,
        )

        communities = current_menu.submenu("communities")
        communities.submenu("requests").register(
            "invenio_communities.communities_requests",
            text=_("Requests"),
            order=2,
            expected_args=["pid_value"],
            **dict(icon="comments", permissions="can_search_requests")
        )
        communities.submenu("members").register(
            "invenio_communities.members",
            text=_("Members"),
            order=3,
            expected_args=["pid_value"],
            **dict(icon="users", permissions="can_read")
        )
        communities.submenu("settings").register(
            "invenio_communities.communities_settings",
            text=_("Settings"),
            order=4,
            expected_args=["pid_value"],
            **dict(icon="settings", permissions="can_update")
        )

    # Register error handlers
    blueprint.register_error_handler(
        PermissionDeniedError, record_permission_denied_error
    )
    blueprint.register_error_handler(PIDDeletedError, record_tombstone_error)
    blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)

    # Register context processor
    blueprint.app_context_processor(search_app_context)

    return blueprint
