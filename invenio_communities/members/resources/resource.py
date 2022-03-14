# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
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
    """Member resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""

        routes = self.config.routes
        return [
            route("GET", routes["item"], self.read),
            route("PATCH", routes["list"], self.bulk_update),
            route("DELETE", routes["list"], self.bulk_delete),
        ]

    @request_view_args
    @response_handler()
    def read(self):
        """Read member."""
        item = self.service.read(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.view_args["member_id"],
        )
        return item.to_dict(), 200

    @request_view_args
    @request_data
    def bulk_update(self):
        """Update member(s)."""
        self.service.bulk_update(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data
        )

        link = self.service.config.links_search["self"]
        location = link.expand(
            None,
            {
                "community_id": resource_requestctx.view_args["pid_value"],
                "api": current_app.config.get('SITE_API_URL', '/api'),
            }
        )

        return "", 204, {"Location": location}

    @request_view_args
    @request_data
    def bulk_delete(self):
        """Delete member(s)."""
        self.service.bulk_delete(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data
        )
        return "", 204
