# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
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
from invenio_records_resources.resources import RecordResourceConfig
from invenio_requests.resources.requests.config import RequestSearchRequestArgsSchema

from invenio_communities.communities.resources.serializer import (
    UICommunityJSONSerializer,
)
from invenio_communities.errors import (
    CommunityFeaturedEntryDoesNotExistError,
    LogoSizeLimitError,
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
    }
)


class CommunityResourceConfig(RecordResourceConfig):
    """Communities resource configuration."""

    blueprint_name = "communities"
    url_prefix = ""

    routes = {
        "communities-prefix": "/communities",
        "user-prefix": "/user/communities",
        "list": "",
        "item": "/<pid_value>",
        "featured-prefix": "/featured",
        "featured-id": "/<featured_id>",
        "community-requests": "/requests",
    }

    request_view_args = {
        **RecordResourceConfig.request_view_args,
        "featured_id": ma.fields.Int(),
    }
    error_handlers = community_error_handlers
    request_community_requests_search_args = RequestSearchRequestArgsSchema

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer()),
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            UICommunityJSONSerializer()
        ),
    }
