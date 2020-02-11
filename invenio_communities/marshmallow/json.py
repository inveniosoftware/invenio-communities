# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""

from __future__ import absolute_import, print_function

import uuid

from invenio_pidstore.models import PersistentIdentifier
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, GenFunction, \
    SanitizedHTML, SanitizedUnicode
from marshmallow import ValidationError, fields, missing, validate

from invenio_communities.api import Community


def pid_from_context_or_rec(data_value, context, **kwargs):
    """Get PID from marshmallow context."""
    pid = (context or {}).get('pid')
    pid_value = getattr(pid, 'pid_value', None) or data_value
    if not pid_value:
        raise ValidationError('Missing data for required field.')
    else:
        if not pid:  # check that the ID is not already taken
            if PersistentIdentifier.query.filter_by(
                    pid_type='comid', pid_value=pid_value).one_or_none():
                raise ValidationError(
                    'ID "{}" is already assigned to a community.'.format(pid_value))
        return pid_value


def load_creator(_, context):
    """Load the record creator."""
    old_data = context.get('record')
    if old_data:
        return old_data.get('created_by', missing)
    # TODO a validation error must be raised in each case
    return context.get('user_id', missing)


def serialize_creator(record, context):
    """Load the record creator."""
    return record.get('created_by', missing)


class CommunitySchemaMetadataV1(StrictKeysMixin):
    """Community metadata schema."""

    schema_ = fields.Str(attribute="$schema", dump_to="$schema")

    id = GenFunction(
        deserialize=pid_from_context_or_rec,
        serialize=pid_from_context_or_rec  # to be added only when loading
    )
    title = SanitizedUnicode(required=True)
    description = SanitizedHTML()
    curation_policy = SanitizedHTML()
    page = SanitizedHTML()
    type = fields.Str(required=True, validate=validate.OneOf([
        'organization',
        'event',
        'topic',
        'project',
    ]))
    alternate_identifiers = fields.List(fields.Raw())
    website = fields.Url()
    funding = fields.List(fields.String())
    domain = fields.List(fields.String())
    verified = fields.Boolean()
    visibility = fields.Str(validate=validate.OneOf([
        'public',
        'private',
        'hidden',
    ]))
    member_policy = fields.Str(validate=validate.OneOf([
        'open',
        'closed',
    ]))
    record_policy = fields.Str(validate=validate.OneOf([
        'open',
        'closed',
        'restricted',
    ]))
    archived = fields.Boolean()
    created_by = GenFunction(
        deserialize=load_creator,
        serialize=serialize_creator
    )


class CommunitySchemaV1(StrictKeysMixin):
    """Schema for the community metadata."""

    created = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Raw(dump_only=True)
    metadata = fields.Nested(CommunitySchemaMetadataV1)
