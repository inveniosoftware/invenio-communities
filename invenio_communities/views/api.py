# SPDX-FileCopyrightText: 2016-2024 CERN.
# SPDX-License-Identifier: MIT

"""API views."""

from flask import Blueprint

blueprint = Blueprint(
    "invenio_communities_ext",
    __name__,
    template_folder="../templates",
)


def create_communities_api_blueprint(app):
    """Create communities api blueprint."""
    ext = app.extensions["invenio-communities"]
    # control blueprint endpoints registration
    return ext.communities_resource.as_blueprint()


def create_members_api_bp_from_app(app):
    """Create members api blueprint."""
    ext = app.extensions["invenio-communities"]
    # control blueprint endpoints registration
    return ext.members_resource.as_blueprint()


def create_subcommunities_api_blueprint(app):
    """Create subcommunities api blueprint."""
    ext = app.extensions["invenio-communities"]
    return ext.subcommunities_resource.as_blueprint()
