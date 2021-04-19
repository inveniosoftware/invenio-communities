# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Communities Resource API."""

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import \
    RecordResource, request_search_args
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
