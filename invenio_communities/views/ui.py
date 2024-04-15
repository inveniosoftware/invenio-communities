# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2023-2024 Graz University of Technology.
# Copyright (C) 2023 KTH Royal Institute of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Communities UI views."""

from datetime import datetime

from babel.dates import format_datetime
from flask import Blueprint, current_app, g, render_template, request, url_for
from flask_login import current_user
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import PermissionDeniedError

from invenio_communities.communities.resources.serializer import (
    UICommunityJSONSerializer,
)
from invenio_communities.proxies import current_communities

from ..errors import CommunityDeletedError
from ..searchapp import search_app_context
from .communities import (
    communities_about,
    communities_curation_policy,
    communities_frontpage,
    communities_new,
    communities_requests,
    communities_search,
    communities_settings,
    communities_settings_curation_policy,
    communities_settings_pages,
    communities_settings_privileges,
    community_theme_css_config,
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
    record = getattr(error, "record", None)
    if (record_ui := getattr(error, "result_item", None)) is not None:
        if record is None:
            record = record_ui._record
        record_ui = UICommunityJSONSerializer().dump_obj(record_ui.to_dict())

    # render a 404 page if the tombstone isn't visible
    if not record.tombstone.is_visible:
        return not_found_error(error)

    # we only render a tombstone page if there is a record with a visible tombstone
    return (
        render_template(
            "invenio_communities/tombstone.html",
            record=record_ui,
        ),
        410,
    )


def record_permission_denied_error(error):
    """Handle permission denier error on record views."""
    if not current_user.is_authenticated:
        # trigger the flask-login unauthorized handler
        return current_app.login_manager.unauthorized()
    return render_template(current_app.config["THEME_403_TEMPLATE"]), 403


def _can_create_community():
    """Function used to check if a user has permissions to create a community."""
    return current_communities.service.check_permission(g.identity, "create")


def _show_create_community_link():
    """
    Determine if the 'New community' button should always be visible.

    If the 'COMMUNITIES_ALWAYS_SHOW_CREATE_LINK' config is False,
    check the user's permission to create a community link. If the config is
    True, the button is always visible.
    """
    should_show = current_app.config.get("COMMUNITIES_ALWAYS_SHOW_CREATE_LINK", False)
    if not should_show:  # show only when user can create
        should_show = _can_create_community()
    return should_show


def _has_about_page_content():
    """Function used to check if about page has content."""
    community = request.community
    if community and "metadata" in community and "page" in community["metadata"]:
        return community["metadata"]["page"] != ""
    return False


def _has_curation_policy_page_content():
    """Function used to check if curation policy page has content."""
    community = request.community
    if (
        community
        and "metadata" in community
        and "curation_policy" in community["metadata"]
    ):
        return community["metadata"]["curation_policy"] != ""
    return False


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
        strict_slashes=False,
    )

    blueprint.add_url_rule(
        routes["search"],
        view_func=communities_search,
        strict_slashes=False,
    )

    blueprint.add_url_rule(
        routes["new"],
        view_func=communities_new,
    )

    blueprint.add_url_rule(
        routes["about"],
        view_func=communities_about,
    )

    blueprint.add_url_rule(
        routes["curation_policy"],
        view_func=communities_curation_policy,
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

    blueprint.add_url_rule(
        routes["settings_curation_policy"],
        view_func=communities_settings_curation_policy,
    )

    blueprint.add_url_rule(
        routes["settings_pages"],
        view_func=communities_settings_pages,
    )

    blueprint.add_url_rule(routes["members"], view_func=members)

    blueprint.add_url_rule(routes["invitations"], view_func=invitations)

    # theme injection view
    blueprint.add_url_rule(
        "/communities/<pid_value>/community-theme-<revision>.css",
        view_func=community_theme_css_config,
    )

    # Register error handlers
    blueprint.register_error_handler(
        PermissionDeniedError, record_permission_denied_error
    )
    blueprint.register_error_handler(CommunityDeletedError, record_tombstone_error)
    blueprint.register_error_handler(PIDDeletedError, record_tombstone_error)
    blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)

    # Register context processor
    blueprint.app_context_processor(search_app_context)

    # Template filters
    @blueprint.app_template_filter()
    def invenio_format_datetime(value):
        date = datetime.fromisoformat(value)
        locale_value = current_app.config.get("BABEL_DEFAULT_LOCALE")
        return format_datetime(date, locale=locale_value)

    @blueprint.app_template_filter("resolve_community_logo")
    def resolve_community_logo(logo_link, community_id):
        """Returns placeholder image link if passed community doesn't have a logo."""
        community_service = current_service_registry.get("communities")

        try:
            community_service.read_logo(
                identity=g.identity,
                id_=community_id,
            )
        except FileNotFoundError:
            return url_for("static", filename="images/square-placeholder.png")

        return logo_link

    return blueprint
