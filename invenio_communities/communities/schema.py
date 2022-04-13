# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community schema."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_vocabularies.contrib.affiliations.schema import \
    AffiliationRelationSchema
from invenio_vocabularies.contrib.awards.schema import FundingRelationSchema
from marshmallow import Schema, fields, validate
from marshmallow_utils.fields import NestedAttribute, SanitizedHTML, \
    SanitizedUnicode


def _not_blank(**kwargs):
    """Returns a non-blank validation rule."""
    max_ = kwargs.get('max','')
    return validate.Length(
        error=_('Field cannot be blank or longer than {max_} characters.'.format(max_=max_)),
        min=1,
        **kwargs
    )


# TODO: Move to Invenio-Records-Resources and make reusable (duplicated from
# Invenio-RDM-Records).
class Agent(Schema):
    """An agent schema."""

    user = fields.Integer(required=True)


class CommunityAccessSchema(Schema):

    owned_by = fields.List(fields.Nested(Agent))

    visibility = fields.Str(validate=validate.OneOf([
        'public',
        'restricted',
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
    description = SanitizedUnicode(validate=_not_blank(max=2000))

    curation_policy = SanitizedHTML(validate=_not_blank(max=2000))
    page = SanitizedHTML(validate=_not_blank(max=2000))

    # TODO: Use general small vocabularies
    type = SanitizedUnicode(
        validate=validate.OneOf(COMMUNITY_TYPES)
    )
    website = fields.Url(validate=_not_blank())
    funding = fields.List(fields.Nested(FundingRelationSchema))
    organizations = fields.List(fields.Nested(AffiliationRelationSchema))

    # TODO: Add when general vocabularies are ready
    # domains = fields.List(fields.Str())


class CommunitySchema(BaseRecordSchema):
    """Schema for the community metadata."""

    id = SanitizedUnicode(required=True, validate=_not_blank(max=100))
    uuid = fields.Method(serialize='get_uuid')
    metadata = NestedAttribute(CommunityMetadataSchema, required=True)
    access = NestedAttribute(CommunityAccessSchema, required=True)

    def get_uuid(self, obj):
        """Get the internal UUID."""
        return str(obj.id)


class CommunityFeaturedSchema(Schema):
    id = fields.Int(metadata={'read_only': True})
    start_date = fields.DateTime(required=True)
