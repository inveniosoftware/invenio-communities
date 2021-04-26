# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Communities Resource API config."""

from flask_resources import HTTPJSONException, create_error_handler
from invenio_records_resources.resources import RecordResourceConfig

community_error_handlers = RecordResourceConfig.error_handlers.copy()
community_error_handlers.update({
    FileNotFoundError: create_error_handler(
        HTTPJSONException(
            code=404,
            description="No logo exists for this community.",
        )
    ),
})


class CommunityResourceConfig(RecordResourceConfig):
    """Communities resource configuration."""

    blueprint_name = "communities"
    url_prefix = ""

    routes = {
        "communities-prefix": "/communities",
        "user-prefix": "/user/communities",
        "list": "",
        "item": "/<pid_value>"
    }

    error_handlers = community_error_handlers
