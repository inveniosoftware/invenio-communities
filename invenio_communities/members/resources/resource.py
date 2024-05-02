# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Resource API."""

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import (
    RecordResource,
    request_data,
    request_extra_args,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference


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
            route("GET", routes["publicmembers"], self.search_public),
            route("POST", routes["invitations"], self.invite),
            route("PUT", routes["invitations"], self.update_invitations),
            route("GET", routes["invitations"], self.search_invitations),
            route("POST", routes["membership_requests"], self.request_membership),
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
            search_preference=search_preference(),
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
            search_preference=search_preference(),
        )
        return hits.to_dict(), 200

    @request_view_args
    @request_search_args
    @response_handler(many=True)
    def search_invitations(self):
        """Perform a search over the invitations."""
        hits = self.service.search_invitations(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            search_preference=search_preference(),
        )
        return hits.to_dict(), 200

    @request_view_args
    @request_data
    def add(self):
        """Add members."""
        self.service.add(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        return "", 204

    @request_view_args
    @request_data
    def invite(self):
        """Invite members."""
        self.service.invite(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        return "", 204

    @request_view_args
    @request_data
    def request_membership(self):
        """Request membership."""
        request = self.service.request_membership(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        return request.to_dict(), 201

    @request_view_args
    @request_extra_args
    @request_data
    def update(self):
        """Update member."""
        self.service.update(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data,
            refresh=resource_requestctx.args.get("refresh", False),
        )
        return "", 204

    @request_view_args
    @request_data
    def update_invitations(self):
        """Update invitations."""
        self.service.update(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data,
        )
        return "", 204

    @request_view_args
    @request_data
    def delete(self):
        """Delete members."""
        self.service.delete(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data,
        )
        return "", 204
