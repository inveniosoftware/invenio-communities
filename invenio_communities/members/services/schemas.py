# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Member schema."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import Schema, fields, validate, validates_schema, \
    ValidationError
from marshmallow_utils.fields import SanitizedUnicode


# TODO find a way to make those more configurable
ROLE_TYPES = [
    "owner",
    "manager",
    "curator",
    "reader"
]


class MemberBulkItemSchema(Schema):
    """Schema for bulk item."""

    # input
    id = fields.Str(required=True)
    revision_id = fields.Integer(required=True)


class MemberBulkSchema(BaseRecordSchema):
    """Schema for bulk member change/delete."""

    # input
    members = fields.List(fields.Nested(MemberBulkItemSchema))
    role = fields.String(
        required=True,
        validate=validate.OneOf(ROLE_TYPES)
    )
    # TODO: add visibility


class MemberUpdateSchema(Schema):
    """Member update schema.

    In this context, all fields are optional.
    """

    role = fields.String(
        validate=validate.OneOf(ROLE_TYPES)
    )
    # TODO: add visibility


class MemberCreationSchema(BaseRecordSchema):
    """Schema for the creation of a community member."""

    # input and output
    community = SanitizedUnicode(required=True)
    user = fields.Integer()
    role = fields.String(
        required=True,
        validate=validate.OneOf(ROLE_TYPES)
    )
    # TODO: add visibility
    # TODO: add group
    # group = SanitizedUnicode()

    @validates_schema
    def validate_member_entity(self, data, **kwargs):
        """Check that at least one member entity is passed."""
        valid_entities = ['user', 'group']

        # TODO?: Could maybe use something like ?
        # validate.OneOf(valid_entities)
        if not any(e in data for e in valid_entities):
            raise ValidationError(
                _("There must be one of {}".format(valid_entities))
            )


class MemberSchema(BaseRecordSchema):
    """Schema for community member otherwise."""

    # input
    role = fields.String(
        required=True,
        validate=validate.OneOf(ROLE_TYPES)
    )

    # output only
    is_current_user = fields.Bool(dump_only=True)
    # TODO: add name
    # name = SanitizedUnicode(dump_only=True)

    # TODO: add visibility
