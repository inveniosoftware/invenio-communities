# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities UI views."""

from flask import Blueprint, current_app, render_template
from flask_login import current_user
from flask_menu import current_menu
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError

from .communities import communities_detail, communities_frontpage, \
    communities_new, communities_search, communities_settings, \
    communities_settings_privileges


#
# Error handlers
#
def not_found_error(error):
    """Handler for 'Not Found' errors."""
    return render_template(current_app.config['THEME_404_TEMPLATE']), 404


def record_tombstone_error(error):
    """Tombstone page."""
    return render_template("invenio_communities/tombstone.html"), 410


def record_permission_denied_error(error):
    """Handle permission denier error on record views."""
    if not current_user.is_authenticated:
        # trigger the flask-login unauthorized handler
        return current_app.login_manager.unauthorized()
    return render_template(current_app.config['THEME_403_TEMPLATE']), 403


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
        static_folder='../static'
    )

    # control blueprint endpoints registration
    if app.config["COMMUNITIES_ENABLED"]:
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

        blueprint.add_url_rule(
            routes["details"],
            view_func=communities_detail,
        )

        # Settings tab routes
        blueprint.add_url_rule(
            routes["settings"],
            view_func=communities_settings,
        )

        blueprint.add_url_rule(
            routes["settings_privileges"],
            view_func=communities_settings_privileges,
        )

        @blueprint.before_app_first_request
        def register_menus():
            """Register community menu items."""
            item = current_menu.submenu('main.communities')
            item.register(
                'invenio_communities.communities_frontpage',
                'Communities',
                order=3,
            )

            item = current_menu.submenu('plus.community').register(
                'invenio_communities.communities_new',
                'New community',
                order=3,
            )

        # Register error handlers
        blueprint.register_error_handler(
            PermissionDeniedError, record_permission_denied_error)
        blueprint.register_error_handler(PIDDeletedError, record_tombstone_error)
        blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)

    return blueprint
