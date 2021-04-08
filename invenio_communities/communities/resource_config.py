# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Communities Resource API config."""

from invenio_records_resources.resources import RecordResourceConfig


class CommunityResourceConfig(RecordResourceConfig):
    """Communities resource configuration."""

    blueprint_name = "communities"
    url_prefix = "/communities"

    routes = {
        "list": "",
        "item": "/<pid_value>"
    }

    links_config= {}
