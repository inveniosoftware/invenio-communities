# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community schema."""

import re
from uuid import UUID

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_vocabularies.contrib.affiliations.schema import AffiliationRelationSchema
from invenio_vocabularies.contrib.awards.schema import FundingRelationSchema
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


# TODO this schema is duplicated from invenio-rdm-records, can't be imported
# TODO in this module. Might need to be moved to invenio-vocabularies.
# TODO move clean method to reusable non-record schema class
class VocabularySchema(Schema):
    """Invenio Vocabulary schema."""

    id = SanitizedUnicode(required=True)
    title = fields.Dict(dump_only=True)

    @pre_load
    def clean(self, data, **kwargs):
        """Removes dump_only fields.

        Why: We want to allow the output of a Schema dump, to be a valid input
             to a Schema load without causing strange issues.
        """
        value_is_dict = isinstance(data, dict)
        if value_is_dict:
            for name, field in self.fields.items():
                if field.dump_only:
                    data.pop(name, None)
        return data


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

    @post_load
    def lowercase(self, in_data, **kwargs):
        """Ensure slug is lowercase."""
        in_data["slug"] = in_data["slug"].lower()
        return in_data


class CommunityFeaturedSchema(Schema):
    """Community Featured Schema."""

    id = fields.Int(metadata={"read_only": True})
    start_date = fields.DateTime(required=True)
