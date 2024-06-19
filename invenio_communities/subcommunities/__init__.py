# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunities module."""

from .resources import SubcommunityRequestResource, SubCommunityResourceConfig
from .services import SubCommunityService, SubCommunityServiceConfig

__all__ = (
    "SubcommunityRequestResource",
    "SubCommunityResourceConfig",
    "SubCommunityService",
    "SubCommunityServiceConfig",
)
