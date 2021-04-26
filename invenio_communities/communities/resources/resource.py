# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Communities Resource API."""

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.files.resource import request_stream
from invenio_records_resources.resources.records.resource import \
    RecordResource, request_data, request_headers, request_search_args, \
    request_view_args
from invenio_records_resources.resources.records.utils import es_preference


class CommunityResource(RecordResource):
    """Communities resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""

        def p(prefix, route):
            """Prefix a route with the URL prefix."""
            return f"{prefix}{route}"

        routes = self.config.routes
        return [
            route(
                "GET",
                p(routes["communities-prefix"], routes["list"]),
                self.search
            ),
            route(
                "POST",
                p(routes["communities-prefix"], routes["list"]),
                self.create
            ),
            route(
                "GET",
                p(routes["communities-prefix"], routes["item"]),
                self.read
            ),
            route(
                "PUT",
                p(routes["communities-prefix"], routes["item"]),
                self.update
            ),
            route(
                "DELETE",
                p(routes["communities-prefix"], routes["item"]),
                self.delete
            ),
            route(
                "GET",
                p(routes["user-prefix"], routes["list"]),
                self.search_user_communities
            ),
            route(
                "POST",
                p(routes["communities-prefix"], routes["item"]) + '/rename',
                self.rename
            ),
            route(
                "GET",
                p(routes["communities-prefix"], routes["item"]) + '/logo',
                self.read_logo
            ),
            route(
                "PUT",
                p(routes["communities-prefix"], routes["item"]) + '/logo',
                self.update_logo
            ),
            route(
                "DELETE",
                p(routes["communities-prefix"], routes["item"]) + '/logo',
                self.delete_logo
            ),
        ]

    @request_search_args
    @response_handler(many=True)
    def search_user_communities(self):
        """Perform a search over the user's communities.

        GET /user/communities
        """
        hits = self.service.search_user_communities(
            identity=g.identity,
            params=resource_requestctx.args,
            es_preference=es_preference()
        )
        return hits.to_dict(), 200

    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def rename(self):
        """Rename a community."""
        item = self.service.rename(
            resource_requestctx.view_args["pid_value"],
            g.identity,
            resource_requestctx.data,
            revision_id=resource_requestctx.headers.get("if_match"),
        )
        return item.to_dict(), 200

    @request_view_args
    def read_logo(self):
        """Read logo's content."""
        item = self.service.read_logo(
            resource_requestctx.view_args["pid_value"],
            g.identity,
        )
        return item.send_file(), 200

    @request_view_args
    @request_stream
    @response_handler()
    def update_logo(self):
        """Upload logo content."""
        item = self.service.update_logo(
            resource_requestctx.view_args["pid_value"],
            g.identity,
            resource_requestctx.data["request_stream"],
            content_length=resource_requestctx.data["request_content_length"],
        )
        return item.to_dict(), 200

    @request_view_args
    def delete_logo(self):
        """Delete logo."""
        self.service.delete_logo(
            resource_requestctx.view_args["pid_value"],
            g.identity,
        )
        return "", 204
