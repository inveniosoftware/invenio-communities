# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitation Resource API."""

from flask import g
from flask_resources import route
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import \
    RecordResource, request_data, request_headers, request_search_args, \
    request_view_args
from invenio_records_resources.resources.records.utils import es_preference


class InvitationResource(RecordResource):
    """Invitation resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        return [
            route("POST", self.config.routes["list"], self.create),
            route("GET", self.config.routes["item"], self.read),
            route("PUT", self.config.routes["item"], self.update),
            route("POST", self.config.routes["action"], self.execute_action),
            route("GET", self.config.routes["list"], self.search),
        ]

    @request_view_args
    @response_handler()
    def read(self):
        """Read an item."""
        item = self.service.read(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.view_args["invitation_id"],
        )
        return item.to_dict(), 200

    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def update(self):
        """Update an item."""
        # not using the community id
        item = self.service.update(
            g.identity,
            resource_requestctx.view_args["invitation_id"],
            resource_requestctx.data,
            revision_id=resource_requestctx.headers.get("if_match"),
        )
        return item.to_dict(), 200

    @request_view_args
    @request_data
    @response_handler()
    def execute_action(self):
        """Execute action."""
        item = self.service.execute_action(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            id_=resource_requestctx.view_args["invitation_id"],
            action=resource_requestctx.view_args["action"],
            data=resource_requestctx.data
        )
        return item.to_dict(), 200

    @request_view_args
    @request_search_args
    @response_handler(many=True)
    def search(self):
        """Perform a search over the items."""
        hits = self.service.search(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            es_preference=es_preference()
        )
        return hits.to_dict(), 200
