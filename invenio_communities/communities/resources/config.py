# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2023      TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Resource API config."""
import marshmallow as ma
from flask_resources import (
    HTTPJSONException,
    JSONSerializer,
    ResponseHandler,
    create_error_handler,
)
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig
from invenio_requests.resources.requests.config import RequestSearchRequestArgsSchema

from invenio_communities.communities.resources.args import (
    CommunitiesSearchRequestArgsSchema,
)
from invenio_communities.communities.resources.serializer import (
    UICommunityJSONSerializer,
)
from invenio_communities.errors import (
    CommunityDeletedError,
    CommunityFeaturedEntryDoesNotExistError,
    LogoSizeLimitError,
    OpenRequestsForCommunityDeletionError,
    SetDefaultCommunityError,
)

community_error_handlers = RecordResourceConfig.error_handlers.copy()
community_error_handlers.update(
    {
        FileNotFoundError: create_error_handler(
            HTTPJSONException(
                code=404,
                description="No logo exists for this community.",
            )
        ),
        CommunityFeaturedEntryDoesNotExistError: create_error_handler(
            lambda e: HTTPJSONException(
                code=404,
                description=str(e),
            )
        ),
        LogoSizeLimitError: create_error_handler(
            lambda e: HTTPJSONException(
                code=400,
                description=str(e),
            )
        ),
        OpenRequestsForCommunityDeletionError: create_error_handler(
            lambda e: HTTPJSONException(
                code=400,
                description=str(e),
            )
        ),
        CommunityDeletedError: create_error_handler(
            lambda e: (
                HTTPJSONException(
                    code=410, description=_("The record has been deleted.")
                )
            )
        ),
        SetDefaultCommunityError: create_error_handler(
            lambda e: HTTPJSONException(
                code=400,
                description=str(e),
            )
        ),
    }
)


class CommunityResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Communities resource configuration."""

    blueprint_name = "communities"
    url_prefix = ""

    routes = {
        "list": "/communities",
        "item": "/communities/<pid_value>",
        "rename": "/communities/<pid_value>/rename",
        "logo": "/communities/<pid_value>/logo",
        "featured-search": "/communities/featured",
        "featured-list": "/communities/<pid_value>/featured",
        "featured-item": "/communities/<pid_value>/featured/<featured_id>",
        "user-communities": "/user/communities",
        "community-requests": "/communities/<pid_value>/requests",
        "restore-community": "/communities/<pid_value>/restore",
    }

    request_search_args = CommunitiesSearchRequestArgsSchema

    request_view_args = {
        **RecordResourceConfig.request_view_args,
        "featured_id": ma.fields.Int(),
    }
    error_handlers = FromConfig(
        "COMMUNITIES_ERROR_HANDLERS", default=community_error_handlers
    )
    request_community_requests_search_args = RequestSearchRequestArgsSchema

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            UICommunityJSONSerializer(), headers=etag_headers
        ),
    }
