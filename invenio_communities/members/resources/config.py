# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Member Resource API config."""

import marshmallow as ma
from flask_resources import HTTPJSONException, create_error_handler
from invenio_records_resources.resources import RecordResourceConfig

from ...errors import CommunityHidden
from ..errors import LastOwnerError, OwnerSelfRoleChangeError


class MemberResourceConfig(RecordResourceConfig):
    """Member resource configuration."""

    blueprint_name = "community_members"
    url_prefix = ""

    routes = {
        "item": "/communities/<pid_value>/members/<member_id>",
        "list": "/communities/<pid_value>/members"
    }
    request_view_args = {
        "pid_value": ma.fields.Str(),
        "member_id": ma.fields.Str(),
    }

    error_handlers = {
        CommunityHidden: create_error_handler(
            HTTPJSONException(
                code=404,
                description="Not found.",
            )
        ),
        # Passing this error as a generic permission error for now
        OwnerSelfRoleChangeError: create_error_handler(
            HTTPJSONException(
                code=403,
                description="Permission denied.",
            )
        ),
        LastOwnerError: create_error_handler(
            HTTPJSONException(
                code=400,
                description="Invalid action.",
            )
        ),

    }
