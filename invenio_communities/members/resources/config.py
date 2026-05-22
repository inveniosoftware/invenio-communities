# SPDX-FileCopyrightText: 2022 KTH Royal Institute of Technology
# SPDX-FileCopyrightText: 2022-2024 Northwestern University.
# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-FileCopyrightText: 2023 TU Wien.
# SPDX-FileCopyrightText: 2024 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""Member Resource API config."""

import marshmallow as ma
from flask_resources import HTTPJSONException, create_error_handler
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.resources import RecordResourceConfig

from ...errors import CommunityDeletedError
from ..errors import AlreadyMemberError, InvalidMemberError


class MemberResourceConfig(RecordResourceConfig):
    """Member resource configuration."""

    blueprint_name = "community_members"
    url_prefix = ""

    routes = {
        "members": "/communities/<pid_value>/members",
        "publicmembers": "/communities/<pid_value>/members/public",
        "invitations": "/communities/<pid_value>/invitations",
        "membership_requests": "/communities/<pid_value>/membership-requests",
    }
    request_view_args = {
        "pid_value": ma.fields.UUID(),
        "member_id": ma.fields.Str(),
    }

    error_handlers = {
        InvalidMemberError: create_error_handler(
            HTTPJSONException(
                code=400,
                description=_("Invalid member specified."),
            )
        ),
        AlreadyMemberError: create_error_handler(
            HTTPJSONException(
                code=400,
                description=_(
                    "One of the submitted entity is already a member or pending a decision. The entire action was cancelled."  # noqa
                ),
            )
        ),
        CommunityDeletedError: create_error_handler(
            lambda e: (
                HTTPJSONException(
                    code=410, description=_("The record has been deleted.")
                )
            )
        ),
    }

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }
