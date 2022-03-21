# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""API views."""


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
