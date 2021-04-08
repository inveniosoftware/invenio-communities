# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

import marshmallow as ma
from flask import g
from flask_resources import JSONDeserializer, RequestBodyParser, \
    request_body_parser, request_parser, resource_requestctx, \
    response_handler, route
from flask_resources.context import resource_requestctx
from invenio_db import db
from invenio_records_resources.resources import RecordResource
from invenio_records_resources.resources.records.resource import \
    request_data, request_search_args, request_view_args
from invenio_records_resources.resources.records.utils import es_preference


class CommunityResource(RecordResource):
    """Communities resource."""

    @request_data
    @response_handler()
    def create(self):
        """Create an item."""
        data = resource_requestctx.data
        item = self.service.create(
            identity=g.identity,
            data=data
        )
        return item.to_dict(), 201

    @request_view_args
    @response_handler()
    def read(self):
        """Retrieve a record."""
        item = self.service.read(
            id_=resource_requestctx.view_args["pid_value"],
            identity=g.identity,
        )
        return item.to_dict(), 200

    @request_view_args
    @request_data
    @response_handler()
    def update(self):
        """Patch a secret link for a record."""
        item = self.service.update(
            id_=resource_requestctx.view_args["pid_value"],
            identity=g.identity,
            data=resource_requestctx.data,
        )
        return item.to_dict(), 200

    @request_view_args
    def delete(self):
        """Delete a a secret link for a record."""
        self.service.delete(
            id_=resource_requestctx.view_args["pid_value"],
            identity=g.identity,
        )
        return "", 204

    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search(self):
        """List secret links for a record."""
        items = self.service.search(
            identity=g.identity,
            params=resource_requestctx.args,
            links_config=self.config.links_config,
            es_preference=es_preference()
        )
        return items.to_dict(), 200

    def create_url_rules(self):
        return [
            route("GET", self.config.routes['item'], self.read),
            route("POST", self.config.routes['list'], self.create),
            route("PUT", self.config.routes['item'], self.update),
            route("DELETE", self.config.routes['item'], self.delete),
            route("GET", self.config.routes['list'], self.search)
        ]
