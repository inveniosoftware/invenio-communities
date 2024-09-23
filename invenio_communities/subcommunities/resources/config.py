# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunity resource configuration."""

from flask_resources import (
    HTTPJSONException,
    JSONDeserializer,
    JSONSerializer,
    RequestBodyParser,
    ResourceConfig,
    ResponseHandler,
    create_error_handler,
)
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.base.config import ConfiguratorMixin
from marshmallow import fields

from invenio_communities.communities.resources.args import (
    CommunitiesSearchRequestArgsSchema,
)
from invenio_communities.communities.resources.serializer import (
    UICommunityJSONSerializer,
)

from ..services.errors import ParentChildrenNotAllowed

json_response_handler = ResponseHandler(JSONSerializer(), headers=etag_headers)


class SubCommunityResourceConfig(ConfiguratorMixin, ResourceConfig):
    """Subcommunity resource configuration."""

    # Blueprint configuration
    blueprint_name = "subcommunities"
    url_prefix = ""
    routes = {
        "join": "/communities/<pid_value>/actions/join-request",
        "list": "/communities/<pid_value>/subcommunities",
    }
    request_view_args = {
        "pid_value": fields.UUID(),
    }

    # Request parsing
    request_read_args = {}
    request_extra_args = {}
    request_body_parsers = {"application/json": RequestBodyParser(JSONDeserializer())}
    default_content_type = "application/json"

    request_search_args = CommunitiesSearchRequestArgsSchema

    # Response handling
    response_handlers = {
        "application/json": json_response_handler,
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            UICommunityJSONSerializer(), headers=etag_headers
        ),
    }
    default_accept_mimetype = "application/json"

    # Error handling
    error_handlers = {
        # Parent community does not allow children
        ParentChildrenNotAllowed: create_error_handler(
            lambda e: HTTPJSONException(
                code=400,
                description=str(e),
            )
        ),
    }
