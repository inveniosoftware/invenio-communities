# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitation Resource API config."""

import marshmallow as ma
from flask_resources import HTTPJSONException, create_error_handler
from invenio_records_resources.resources import RecordResourceConfig

invitation_error_handlers = RecordResourceConfig.error_handlers.copy()
# community_error_handlers.update({
#     FileNotFoundError: create_error_handler(
#         HTTPJSONException(
#             code=404,
#             description="No logo exists for this community.",
#         )
#     ),
# })


class InvitationResourceConfig(RecordResourceConfig):
    """Communities resource configuration."""

    blueprint_name = "community_invitations"
    url_prefix = ""

    routes = {
        "list": "/communities/<pid_value>/invitations",
        "item": "/communities/<pid_value>/invitations/<invitation_id>",
        "action": "/communities/<pid_value>/invitations/<invitation_id>/actions/<action>",  # noqa
    }
    request_view_args = {
        "pid_value": ma.fields.Str(),
        "invitation_id": ma.fields.Str(),
        "action": ma.fields.Str(),
    }

    error_handlers = invitation_error_handlers
