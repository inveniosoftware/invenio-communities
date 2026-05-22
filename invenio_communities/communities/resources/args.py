# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Schemas for parameter parsing."""

from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from marshmallow import fields


class CommunitiesSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Extend schema with CSL fields."""

    status = fields.Str()
    include_deleted = fields.Bool()
