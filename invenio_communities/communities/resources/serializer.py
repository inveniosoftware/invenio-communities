# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Invenio Communities Resource Serializers."""

from flask_resources import BaseListSchema, JSONSerializer, MarshmallowSerializer

from invenio_communities.communities.resources.ui_schema import UICommunitySchema


class UICommunityJSONSerializer(MarshmallowSerializer):
    """UI Community JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UICommunitySchema,
            list_schema_cls=BaseListSchema,
        )
