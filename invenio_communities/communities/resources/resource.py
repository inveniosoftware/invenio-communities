# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Resource API."""

from flask import g
from flask_resources import from_conf, request_parser, resource_requestctx, \
    response_handler, route
from invenio_records_resources.resources.files.resource import request_stream
from invenio_records_resources.resources.records.resource import \
    RecordResource, request_data, request_headers, request_search_args, \
    request_view_args
from invenio_records_resources.resources.records.utils import es_preference


request_community_requests_search_args = request_parser(
    from_conf('request_community_requests_search_args'), location='args'
)

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
            route(
                "GET",
                p(routes["communities-prefix"], routes["featured-prefix"]),
                self.featured_communities_search
            ),
            route(
                "GET",
                p(routes["communities-prefix"], routes["item"]) + routes["featured-prefix"],
                self.featured_list
            ),
            route(
                "POST",
                p(routes["communities-prefix"], routes["item"]) + routes["featured-prefix"],
                self.featured_create
            ),
            route(
                "PUT",
                p(routes["communities-prefix"], routes["item"]) + p(routes["featured-prefix"], routes["featured-id"]),
                self.featured_update
            ),
            route(
                "DELETE",
                p(routes["communities-prefix"], routes["item"]) + p(routes["featured-prefix"], routes["featured-id"]),
                self.featured_delete
            ),
            route(
                "GET",
                p(routes["communities-prefix"], routes["item"] + routes["community-requests"]),
                self.search_community_requests
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

    @request_view_args
    @request_community_requests_search_args
    @response_handler(many=True)
    def search_community_requests(self):
        """Perform a search over the community's requests.

        GET /communities/<pid_value>/requests
        """
        hits = self.service.search_community_requests(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
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
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
            revision_id=resource_requestctx.headers.get("if_match"),
        )
        return item.to_dict(), 200

    @request_view_args
    def read_logo(self):
        """Read logo's content."""
        item = self.service.read_logo(
            g.identity,
            resource_requestctx.view_args["pid_value"],
        )
        return item.send_file(), 200

    @request_view_args
    @request_stream
    @response_handler()
    def update_logo(self):
        """Upload logo content."""
        item = self.service.update_logo(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data["request_stream"],
            content_length=resource_requestctx.data["request_content_length"],
        )
        return item.to_dict(), 200

    @request_view_args
    def delete_logo(self):
        """Delete logo."""
        self.service.delete_logo(
            g.identity,
            resource_requestctx.view_args["pid_value"],
        )
        return "", 204

    @request_search_args
    @response_handler(many=True)
    def featured_communities_search(self):
        hits = self.service.featured_search(
            identiy=g.identity,
            params=resource_requestctx.args,
            es_preference=es_preference(),
        )
        return hits.to_dict(), 200

    @request_headers
    @request_view_args
    @response_handler()
    def featured_list(self):
        """List featured entries for a community."""
        items = self.service.featured_list(
            g.identity,
            resource_requestctx.view_args["pid_value"],
        )
        return items.to_dict(), 200


    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def featured_create(self):
        """Create a featured community entry."""
        item = self.service.featured_create(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        return item.to_dict(), 201

    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def featured_update(self):
        """Update a featured community entry."""
        item = self.service.featured_update(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
            featured_id=resource_requestctx.view_args["featured_id"],
        )
        return item.to_dict(), 200

    @request_view_args
    def featured_delete(self):
        """Delete a featured community entry."""
        self.service.featured_delete(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            featured_id=resource_requestctx.view_args["featured_id"],
        )
        return "", 204
