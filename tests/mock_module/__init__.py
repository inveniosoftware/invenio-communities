# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
# Copyright (C) 2026 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Mock module."""

from flask import Blueprint
from invenio_administration.views.base import (
    AdminResourceListView,
)


def create_invenio_app_rdm_communities_blueprint(app):
    """Create fake invenio_app_rdm_communities Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_communities",
        __name__,
    )

    def communities_home(pid_value, community, community_ui):
        return "<communities home>"

    # Requests URL rules
    blueprint.add_url_rule("/communities/<pid_value>", view_func=communities_home)

    return blueprint


def create_community_records_blueprint(app):
    """Create fake invenio-records Blueprint akin to invenio-rdm-records'."""
    blueprint = Blueprint(
        "community-records",
        __name__,
    )

    def search():
        return "<search>"

    blueprint.add_url_rule("/communities/<pid_value>/records", view_func=search)

    return blueprint


def create_community_collections_blueprint(app):
    """Create fake invenio-records Blueprint akin to invenio-rdm-records'."""
    blueprint = Blueprint(
        "collections",
        __name__,
    )

    def list_trees():
        return "<list_trees>"

    blueprint.add_url_rule(
        "/communities/<pid_value>/collection-trees", view_func=list_trees
    )

    return blueprint


def create_invenio_app_rdm_requests_blueprint(app):
    """Create fake invenio_app_rdm_requests Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_requests",
        __name__,
    )

    @blueprint.route("/me/requests/<uuid:request_pid_value>")
    def user_dashboard_request_view(request_pid_value):
        """Fake user_dashboard_request_view."""
        return "<user dashboard request view>"

    @blueprint.route("/communities/<pid_value>/invitations/<uuid:request_pid_value>")
    def community_dashboard_request_view(request_pid_value):
        """Fake community_dashboard_request_view.

        `community_dashboard_request_view` is the view function used to serve the
        invitation endpoint in invenio-app-rdm at time of writing.
        """
        return "<community dashboard invitation view>"

    @blueprint.route(
        "/communities/<pid_value>/membership-requests/<uuid:request_pid_value>"
    )
    def community_dashboard_membership_request_view(request_pid_value):
        """Fake community_dashboard_membership_request_view."""
        return "<community dashboard membership request view>"

    return blueprint


class RecordAdminListView(AdminResourceListView):
    """Configuration for the records list view."""

    name = "records"
    resource_config = "records_resource"


class DraftAdminListView(AdminResourceListView):
    """Configuration for the drafts list view."""

    name = "drafts"
    resource_config = "records_resource"


class UserModerationListView(AdminResourceListView):
    """User moderation admin search view."""

    name = "moderation"
    resource_config = "requests_resource"
