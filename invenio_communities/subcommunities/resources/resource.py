# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunities resource."""

from flask import g
from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference


class SubCommunityResource(ErrorHandlersMixin, Resource):
    """Subcommunity request resource."""

    def __init__(self, config, service):
        """Instantiate the resource with a given configuration and service."""
        super().__init__(config)
        self.service = service

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        url_rules = [
            route("POST", routes["join"], self.join),
            route("GET", routes["list"], self.search),
        ]
        return url_rules

    @request_view_args
    @response_handler()
    @request_data
    def join(self):
        """Join with a subcommunity."""
        result = self.service.join(
            identity=g.identity,
            id_=resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data,
        )
        return result.to_dict(), 201

    @request_view_args
    @response_handler(many=True)
    @request_extra_args
    @request_search_args
    def search(self):
        """List subcommunities."""
        result = self.service.search(
            identity=g.identity,
            id_=resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            search_preference=search_preference(),
            expand=resource_requestctx.args.get("expand", False),
        )
        return result.to_dict(), 200
