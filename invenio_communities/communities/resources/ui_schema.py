# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2023 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI community schema."""

from functools import partial

from flask import g
from flask_resources import BaseObjectSchema
from invenio_i18n import get_locale
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import CustomFieldsSchemaUI
from invenio_vocabularies.contrib.awards.serializer import AwardL10NItemSchema
from invenio_vocabularies.contrib.funders.serializer import FunderL10NItemSchema
from invenio_vocabularies.resources import VocabularyL10Schema
from marshmallow import Schema, fields, post_dump
from marshmallow_utils.fields import FormatEDTF as FormatEDTF_

from invenio_communities.communities.schema import CommunityThemeSchema
from invenio_communities.proxies import current_communities


def _community_permission_check(action, community, identity):
    """Check community permission for identity."""
    try:
        community_id = getattr(community, "id", community["id"])
    except KeyError:
        community_id = getattr(
            community["processed"][0],
            "community_id",
            community["processed"][0]["community_id"],
        )

    return current_communities.service.config.permission_policy_cls(
        action,
        community_id=community_id,
        record=community,
    ).allows(identity)


def mask_removed_by(obj):
    """Mask information about who removed the community."""
    return_value = _("Unknown")
    removed_by = obj.get("removed_by", None)

    if removed_by is not None:
        user = removed_by.get("user", None)

        if user == "system":
            return_value = _("System (automatic)")
        elif user is not None:
            return_value = _("Admin")

    return return_value


# Partial to make short definitions in below schema.
FormatEDTF = partial(FormatEDTF_, locale=get_locale)


class TombstoneSchema(Schema):
    """Schema for a record tombstone."""

    removal_reason = fields.Nested(VocabularyL10Schema, attribute="removal_reason")

    note = fields.String(attribute="note")

    removed_by = fields.Function(mask_removed_by)

    removal_date_l10n_medium = FormatEDTF(attribute="removal_date", format="medium")

    removal_date_l10n_long = FormatEDTF(attribute="removal_date", format="long")

    citation_text = fields.String(attribute="citation_text")

    is_visible = fields.Boolean(attribute="is_visible")


class FundingSchema(Schema):
    """Schema for dumping types in the UI."""

    award = fields.Nested(AwardL10NItemSchema)
    funder = fields.Nested(FunderL10NItemSchema)


class UICommunitySchema(BaseObjectSchema):
    """Schema for dumping extra information of the community for the UI."""

    type = fields.Nested(VocabularyL10Schema, attribute="metadata.type")

    funding = fields.List(
        fields.Nested(FundingSchema()),
        attribute="metadata.funding",
    )

    tombstone = fields.Nested(TombstoneSchema, attribute="tombstone")

    theme = fields.Nested(CommunityThemeSchema, dump_only=True, load_default={})

    # Custom fields
    custom_fields = fields.Nested(
        partial(CustomFieldsSchemaUI, fields_var="COMMUNITIES_CUSTOM_FIELDS")
    )

    permissions = fields.Method("get_permissions", dump_only=True)

    def get_permissions(self, obj):
        """Get permission."""
        if obj == {}:
            return {}

        can_include_directly = _community_permission_check(
            "include_directly", community=obj, identity=g.identity
        )
        can_update = _community_permission_check(
            "update", community=obj, identity=g.identity
        )
        can_submit_record = _community_permission_check(
            "submit_record", community=obj, identity=g.identity
        )
        return {
            "can_include_directly": can_include_directly,
            "can_update": can_update,
            "can_submit_record": can_submit_record,
        }

    @post_dump(pass_original=True)
    def post_dump(self, data, original, many, **kwargs):
        """Pop tombstone field if not deleted/visible."""
        is_deleted = (original.get("deletion_status") or {}).get("is_deleted", False)
        tombstone_visible = (original.get("tombstone") or {}).get("is_visible", True)

        if not is_deleted or not tombstone_visible:
            data.pop("tombstone", None)

        return data


class TypesSchema(Schema):
    """Schema for dumping types in the UI."""

    types = fields.List(fields.Nested(VocabularyL10Schema), attribute="types")
