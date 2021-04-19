# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Community schema."""

from flask_babelex import lazy_gettext as _
from flask import current_app
from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import Schema, fields, missing, validate
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode
from invenio_rdm_records.services.schemas.metadata import FundingSchema, AffiliationSchema


def _not_blank(**kwargs):
    """Returns a non-blank validation rule."""
    return validate.Length(error=_('Cannot be blank.'), min=1, **kwargs)


class CommunityAccessSchema(Schema):

    visibility = fields.Str(validate=validate.OneOf([
        'public',
        'private',
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


class CommunityMetadataSchema(Schema):
    """Community metadata schema."""

    COMMUNITY_TYPES = [
        'organization',
        'event',
        'topic',
        'project',
    ]

    title = SanitizedUnicode(required=True, validate=_not_blank(max=250))
    description = SanitizedHTML(validate=_not_blank(max=2000))

    curation_policy = SanitizedHTML(validate=_not_blank(max=2000))
    page = SanitizedHTML(validate=_not_blank(max=2000))

    # TODO: Use general small vocabularies
    type = SanitizedUnicode(
        required=True,
        validate=validate.OneOf(COMMUNITY_TYPES)
    )
    website = fields.Url(validate=_not_blank())
    funding = fields.List(fields.Nested(FundingSchema))
    affiliations = fields.List(fields.Nested(AffiliationSchema))

    # TODO: Add when general vocabularies are ready
    # domains = fields.List(fields.Str())


class CommunitySchema(BaseRecordSchema):
    """Schema for the community metadata."""

    id = SanitizedUnicode(validate=_not_blank(max=100))
    metadata = fields.Nested(CommunityMetadataSchema, required=True)
    access = fields.Nested(CommunityAccessSchema, required=True)
