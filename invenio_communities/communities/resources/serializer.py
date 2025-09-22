# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Resource Serializers."""

from flask_resources import BaseListSchema, JSONSerializer, MarshmallowSerializer

from .ui_schema import UICommunitySchema


class UICommunityJSONSerializer(MarshmallowSerializer):
    """UI Community JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UICommunitySchema,
            list_schema_cls=BaseListSchema,
        )
