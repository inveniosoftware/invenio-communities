# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Views."""


def create_communities_bp(app):
    """Create communities blueprint."""
    ext = app.extensions["invenio-communities"]
    return ext.communities_resource.as_blueprint()
