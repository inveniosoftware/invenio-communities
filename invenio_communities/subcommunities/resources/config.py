# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunity resource configuration."""
from flask_resources import (
    JSONDeserializer,
    JSONSerializer,
    RequestBodyParser,
    ResourceConfig,
    ResponseHandler,
)
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.base.config import ConfiguratorMixin
from marshmallow import fields


class SubCommunityResourceConfig(ConfiguratorMixin, ResourceConfig):
    """Subcommunity resource configuration."""

    # Blueprint configuration
    blueprint_name = "subcommunities"
    url_prefix = ""
    routes = {
        "join": "/communities/<pid_value>/actions/join-request",
    }
    request_view_args = {
        "pid_value": fields.UUID(),
    }

    # Request parsing
    request_read_args = {}
    request_extra_args = {}
    request_body_parsers = {"application/json": RequestBodyParser(JSONDeserializer())}
    default_content_type = "application/json"

    # Response handling
    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers)
    }
    default_accept_mimetype = "application/json"
