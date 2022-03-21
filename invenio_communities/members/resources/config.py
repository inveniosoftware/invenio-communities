# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Member Resource API config."""

import marshmallow as ma
from flask_resources import HTTPJSONException, create_error_handler
from invenio_records_resources.resources import RecordResourceConfig

from ..errors import AlreadyMemberError, InvalidMemberError


class MemberResourceConfig(RecordResourceConfig):
    """Member resource configuration."""

    blueprint_name = "community_members"
    url_prefix = ""

    routes = {
        "members": "/communities/<pid_value>/members",
        "publicmembers": "/communities/<pid_value>/members/public",
        "invitations": "/communities/<pid_value>/invitations",
    }
    request_view_args = {
        "pid_value": ma.fields.Str(),
        "member_id": ma.fields.Str(),
    }

    error_handlers = {
        InvalidMemberError: create_error_handler(
            HTTPJSONException(
                code=400,
                description="Invalid member specified.",
            )
        ),
        AlreadyMemberError: create_error_handler(
            HTTPJSONException(
                code=400,
                description="A member was already added or invited.",
            )
        ),
    }
