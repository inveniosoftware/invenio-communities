# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Resource API."""

from flask import current_app, g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.files.resource import request_stream
from invenio_records_resources.resources.records.resource import \
    RecordResource, request_data, request_headers, request_search_args, \
    request_view_args
from invenio_records_resources.resources.records.utils import es_preference
from invenio_records_resources.services import Link


class MemberResource(RecordResource):
    """Members resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            route("POST", routes["members"], self.add),
            route("DELETE", routes["members"], self.delete),
            route("PUT", routes["members"], self.update),
            route("GET", routes["members"], self.search),
            route("POST", routes["invitations"], self.invite),
            route("GET", routes["publicmembers"], self.search_public),
        ]

    @request_view_args
    @request_search_args
    @response_handler(many=True)
    def search(self):
        """Perform a search over the items."""
        hits = self.service.search(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            es_preference=es_preference()
        )
        return hits.to_dict(), 200

    @request_view_args
    @request_search_args
    @response_handler(many=True)
    def search_public(self):
        """Perform a search over the items."""
        hits = self.service.search_public(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            es_preference=es_preference()
        )
        return hits.to_dict(), 200

    @request_view_args
    @request_data
    def add(self):
        """Add members."""
        self.service.add(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data
        )
        return "", 204

    @request_view_args
    @request_data
    def invite(self):
        """Invite members."""
        self.service.invite(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data
        )
        return "", 204

    @request_view_args
    @request_data
    def update(self):
        """Update member."""
        self.service.update(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data
        )
        return "", 204


    @request_view_args
    @request_data
    def delete(self):
        """Delete members."""
        self.service.delete(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data
        )
        return "", 204
