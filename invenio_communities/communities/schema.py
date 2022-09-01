# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community schema."""

import re
from functools import partial
from uuid import UUID

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_vocabularies.contrib.affiliations.schema import AffiliationRelationSchema
from invenio_vocabularies.contrib.awards.schema import FundingRelationSchema
from invenio_vocabularies.services.schema import (
    VocabularyRelationSchema as VocabularySchema,
)
from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    post_load,
    pre_load,
    validate,
)
from marshmallow_utils.fields import NestedAttribute, SanitizedHTML, SanitizedUnicode


def _not_blank(**kwargs):
    """Returns a non-blank validation rule."""
    max_ = kwargs.get("max", "")
    return validate.Length(
        error=_(
            "Field cannot be blank or longer than {max_} characters.".format(max_=max_)
        ),
        min=1,
        **kwargs
    )


def is_not_uuid(value):
    """Make sure value is not a UUID."""
    try:
        UUID(value)
        raise ValidationError(
            _("The ID must not be an Universally Unique IDentifier (UUID).")
        )
    except (ValueError, TypeError):
        pass


class CommunityAccessSchema(Schema):
    """Community Access Schema."""

    visibility = fields.Str(
        validate=validate.OneOf(
            [
                "public",
                "restricted",
            ]
        )
    )
    member_policy = fields.Str(
        validate=validate.OneOf(
            [
                "open",
                "closed",
            ]
        )
    )
    record_policy = fields.Str(
        validate=validate.OneOf(
            [
                "open",
                "closed",
                "restricted",
            ]
        )
    )


class CommunityMetadataSchema(Schema):
    """Community metadata schema."""

    title = SanitizedUnicode(required=True, validate=_not_blank(max=250))
    description = SanitizedUnicode(validate=_not_blank(max=2000))

    curation_policy = SanitizedHTML(validate=_not_blank(max=2000))
    page = SanitizedHTML(validate=_not_blank(max=2000))

    type = fields.Nested(VocabularySchema)
    website = fields.Url(validate=_not_blank())
    funding = fields.List(fields.Nested(FundingRelationSchema))
    organizations = fields.List(fields.Nested(AffiliationRelationSchema))

    # TODO: Add when general vocabularies are ready
    # domains = fields.List(fields.Str())


class CommunitySchema(BaseRecordSchema):
    """Schema for the community metadata."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    id = fields.String(dump_only=True)
    slug = SanitizedUnicode(
        required=True,
        validate=[
            _not_blank(max=100),
            validate.Regexp(
                r"^[-\w]+$",
                flags=re.ASCII,
                error=_("The ID should contain only letters with numbers or dashes."),
            ),
            is_not_uuid,
        ],
    )
    metadata = NestedAttribute(CommunityMetadataSchema, required=True)
    access = NestedAttribute(CommunityAccessSchema, required=True)
    custom_fields = NestedAttribute(
        partial(CustomFieldsSchema, fields_var="COMMUNITIES_CUSTOM_FIELDS")
    )

    @pre_load
    def initialize_custom_fields(self, data, **kwargs):
        """Ensure custom fields are initialized.

        We need to do that so that validation can take place in case a configured
        field is marked as required.
        """
        data.setdefault("custom_fields", {})
        return data

    @post_load
    def lowercase(self, in_data, **kwargs):
        """Ensure slug is lowercase."""
        in_data["slug"] = in_data["slug"].lower()
        return in_data


class CommunityFeaturedSchema(Schema):
    """Community Featured Schema."""

    id = fields.Int(metadata={"read_only": True})
    start_date = fields.DateTime(required=True)
