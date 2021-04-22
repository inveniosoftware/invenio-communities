# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities UI views."""

from flask import Blueprint
from flask_menu import current_menu

from .communities import communities_detail, communities_frontpage, \
    communities_new, communities_search, communities_settings, \
    communities_settings_privileges


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

    def register_menu():
        """."""
        item = current_menu.submenu('main.communities')
        item.register(
            'invenio_communities.communities_frontpage',
            'Communities',
            order=3,
        )
        return item

    blueprint.before_app_first_request(register_menu)

    return blueprint
