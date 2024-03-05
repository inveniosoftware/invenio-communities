# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community schema."""
import re
from functools import partial
from uuid import UUID

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from invenio_records_resources.services.records.schema import (
    BaseGhostSchema,
    BaseRecordSchema,
)
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
    post_dump,
    post_load,
    pre_load,
    validate,
)
from marshmallow_utils.fields import (
    URL,
    ISODateString,
    NestedAttribute,
    SanitizedHTML,
    SanitizedUnicode,
)
from marshmallow_utils.permissions import FieldPermissionsMixin


def _not_blank(**kwargs):
    """Returns a non-blank validation rule."""
    max_ = kwargs.get("max", "")
    return validate.Length(
        error=_(
            "Field cannot be blank or longer than {max_} characters.".format(max_=max_)
        ),
        min=1,
        **kwargs,
    )


def no_longer_than(max, **kwargs):
    """Returns a character limit validation rule."""
    return validate.Length(
        error=_("Field cannot be longer than {max} characters.".format(max=max)),
        max=max,
        **kwargs,
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
    members_visibility = fields.Str(
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
    review_policy = fields.Str(
        validate=validate.OneOf(
            [
                "open",
                "closed",
            ]
        )
    )


class CommunityMetadataSchema(Schema):
    """Community metadata schema."""

    title = SanitizedUnicode(required=True, validate=_not_blank(max=250))
    description = SanitizedUnicode(validate=_not_blank(max=250))

    curation_policy = SanitizedHTML(validate=no_longer_than(max=50000))
    page = SanitizedHTML(validate=no_longer_than(max=50000))

    type = fields.Nested(VocabularySchema, metadata={"type": "communitytypes"})
    website = URL(validate=_not_blank())
    funding = fields.List(fields.Nested(FundingRelationSchema))
    organizations = fields.List(fields.Nested(AffiliationRelationSchema))

    # TODO: Add when general vocabularies are ready
    # domains = fields.List(fields.Str())


class AgentSchema(Schema):
    """An agent schema, using a string for the ID to allow the "system" user."""

    user = fields.String(required=True)


class RemovalReasonSchema(VocabularySchema):
    """Schema for the removal reason."""

    id = fields.String(required=True)


class TombstoneSchema(Schema):
    """Schema for the record's tombstone."""

    removal_reason = fields.Nested(RemovalReasonSchema)
    note = SanitizedUnicode()
    removed_by = fields.Nested(AgentSchema, dump_only=True)
    removal_date = ISODateString(dump_only=True)
    citation_text = SanitizedUnicode()
    is_visible = fields.Boolean()


class DeletionStatusSchema(Schema):
    """Schema for the record deletion status."""

    is_deleted = fields.Boolean(dump_only=True)
    status = fields.String(dump_only=True)


class CommunityThemeStyleSchema(Schema):
    """Community Theme configuration schema."""

    font = fields.Dict()
    primaryColor = fields.Str()
    secondaryColor = fields.Str()
    tertiaryColor = fields.Str()
    primaryTextColor = fields.Str()
    secondaryTextColor = fields.Str()
    tertiaryTextColor = fields.Str()
    mainHeaderBackgroundColor = fields.Str()


class CommunityThemeSchema(Schema):
    """Community theme schema."""

    style = fields.Nested(CommunityThemeStyleSchema)
    brand = fields.Str()
    enabled = fields.Boolean()


class ChildrenSchema(Schema):
    """Children schema."""

    allow = fields.Boolean()


class BaseCommunitySchema(BaseRecordSchema, FieldPermissionsMixin):
    """Base schema for the community metadata."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    field_dump_permissions = {
        # hide 'is_verified' behind a permission
        "is_verified": "moderate",
    }

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

    is_verified = fields.Boolean(dump_only=True)

    theme = fields.Nested(CommunityThemeSchema, allow_none=True)

    tombstone = fields.Nested(TombstoneSchema, dump_only=True)

    deletion_status = fields.Nested(DeletionStatusSchema, dump_only=True)

    children = NestedAttribute(ChildrenSchema)

    @post_dump
    def post_dump(self, data, many, **kwargs):
        """Hide tombstone info if the record isn't deleted and metadata if it is."""
        is_deleted = (data.get("deletion_status") or {}).get("is_deleted", False)
        tombstone_visible = (data.get("tombstone") or {}).get("is_visible", True)

        if data.get("custom_fields") is None:
            data.pop("custom_fields", None)

        if data.get("theme") is None:
            data.pop("theme", None)

        if not is_deleted or not tombstone_visible:
            data.pop("tombstone", None)

        return data


class CommunityParentSchema(BaseCommunitySchema):
    """Community parent schema."""


class CommunitySchema(BaseCommunitySchema):
    """Community schema."""

    parent = NestedAttribute(CommunityParentSchema, dump_only=True, allow_none=True)

    @post_dump
    def post_dump(self, data, many, **kwargs):
        """Hide parent field if it's not present."""
        data = super().post_dump(data, many, **kwargs)
        if data.get("parent") is None:
            data.pop("parent", None)
        return data

    @post_load(pass_original=True)
    def filter_parent_id(self, in_data, original_data, **kwargs):
        """Simply keep the parent id."""
        if "parent" in original_data:
            in_data["parent"] = (
                dict(id=original_data["parent"]["id"])
                if original_data["parent"]
                else None
            )
        return in_data

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
    """Community Featured schema."""

    id = fields.Int(dump_only=True)
    start_date = fields.DateTime(
        required=True,
        title="start date",
        description="Accepted format: YYYY-MM-DD hh:mm",
        placeholder="YYYY-MM-DD hh:mm",
    )


class CommunityGhostSchema(BaseGhostSchema):
    """Community ghost schema."""

    id = SanitizedUnicode(dump_only=True)
    metadata = fields.Constant(
        {
            "title": _("Deleted community"),
            "description": _("The community was deleted."),
        },
        dump_only=True,
    )
