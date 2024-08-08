# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunities service schemas."""

from marshmallow import Schema, ValidationError, fields, post_load, pre_load


class MinimalCommunitySchema(Schema):
    """Minimal community schema."""

    slug = fields.String(required=True)
    title = fields.String(required=True)

    @post_load
    def load_default(self, data, **kwargs):
        """Load default values for a community."""
        return {
            "slug": data["slug"],
            "metadata": {
                "title": data["title"],
            },
            "access": {
                "visibility": "public",
                "members_visibility": "public",
                "member_policy": "open",
                "record_submission_policy": "open",
            },
        }


class SubcommunityRequestSchema(Schema):
    """Schema for subcommunity requests."""

    # Community input
    community_id = fields.String()
    community = fields.Nested(MinimalCommunitySchema)

    # community_id or community should be required
    @pre_load
    def validate(self, data, **kwargs):
        """Validate that either community_id or community is provided."""
        if "community_id" not in data and "community" not in data:
            raise ValidationError(
                "Either community_id or community should be provided."
            )
        return data
