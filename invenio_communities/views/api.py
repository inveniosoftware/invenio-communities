# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""API views."""

from flask import Blueprint


def create_communities_api_blueprint(app):
    """Create communities api blueprint."""
    ext = app.extensions["invenio-communities"]
    # control blueprint endpoints registration
    if app.config["COMMUNITIES_ENABLED"]:
        return ext.communities_resource.as_blueprint()
    else:
        # return dummy blueprint
        return Blueprint(
            "invenio_communities_api",
            __name__,
        )
