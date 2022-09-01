# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI community schema."""

from functools import partial

from flask_resources import BaseObjectSchema
from invenio_records_resources.services.custom_fields import CustomFieldsSchemaUI
from invenio_vocabularies.contrib.awards.serializer import AwardL10NItemSchema
from invenio_vocabularies.contrib.funders.serializer import FunderL10NItemSchema
from invenio_vocabularies.resources import VocabularyL10Schema
from marshmallow import Schema, fields


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

    # Custom fields
    custom_fields = fields.Nested(
        partial(CustomFieldsSchemaUI, fields_var="COMMUNITIES_CUSTOM_FIELDS")
    )


class TypesSchema(Schema):
    """Schema for dumping types in the UI."""

    types = fields.List(fields.Nested(VocabularyL10Schema), attribute="types")
