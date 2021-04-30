# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
