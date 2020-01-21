from __future__ import absolute_import, print_function
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""


import uuid

from marshmallow import fields, missing, validate

from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, GenFunction, \
    PersistentIdentifier, SanitizedUnicode

from invenio_communities.proxies import current_communities
from invenio_communities.api import Community


def pid_from_context_or_rec(data_value, context, **kwargs):
    """Get PID from marshmallow context."""
    field_name = 'id'
    pid = (context or {}).get('pid')
    pid_value = getattr(pid, 'pid_value', None) or data_value
    if not pid_value:
        raise Exception('{0} is a required field'.format(field_name))
    else:
        return pid_value


def schema_from_class(_, context):
    """Get the record's schema from context."""
    record = (context or {}).get('record', {})
    return record.get(
        "_schema",
        current_jsonschemas.path_to_url(Community.schema)
    )


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
    id = GenFunction(
        deserialize=pid_from_context_or_rec,
        serialize=pid_from_context_or_rec  # to be added only when loading
    )
    title = SanitizedUnicode(required=True)
    description = fields.Str()
    type = fields.Str(validate=validate.OneOf([
        'organization',
        'event',
        'topic',
        'project',
    ]))
    alternate_identifiers = fields.List(fields.String())
    curation_policy = fields.Str()
    page = fields.Str()
    website = fields.Str()
    funding = fields.List(fields.String())
    domain = fields.Str()
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
    logo = fields.Str()
    schema_ = GenFunction(
        attribute="$schema",
        data_key="$schema",
        deserialize=schema_from_class,
        load_only=True  # to be added only when loading
    )
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
