# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""API views."""

from flask import Blueprint

blueprint = Blueprint(
    "invenio_communities_ext",
    __name__,
    template_folder="../templates",
)


@blueprint.record_once
def init(state):
    """Init app."""
    app = state.app
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    rr_ext = app.extensions["invenio-records-resources"]
    idx_ext = app.extensions["invenio-indexer"]
    ext = app.extensions["invenio-communities"]

    # services
    rr_ext.registry.register(ext.service, service_id="communities")
    rr_ext.registry.register(ext.service.members, service_id="members")

    # indexers
    idx_ext.registry.register(ext.service.indexer, indexer_id="communities")
    idx_ext.registry.register(ext.service.members.indexer, indexer_id="members")
    idx_ext.registry.register(
        ext.service.members.archive_indexer, indexer_id="archived-invitations"
    )

    # change notification handlers
    rr_ext.notification_registry.register("users", ext.service.on_relation_update)


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
