# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Schemas for parameter parsing."""


from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from marshmallow import fields


class CommunitiesSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Extend schema with CSL fields."""

    status = fields.Str()
    include_deleted = fields.Bool()
