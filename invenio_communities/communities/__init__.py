# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community Service API."""

from .resources import CommunityResource, CommunityResourceConfig
from .services import (
    CommunityFileServiceConfig,
    CommunityService,
    CommunityServiceConfig,
    DefaultCommunityComponents,
    SearchOptions,
)

__all__ = (
    "CommunityService",
    "CommunityServiceConfig",
    "CommunityFileServiceConfig",
    "CommunityResource",
    "CommunityResourceConfig",
    "SearchOptions",
    "DefaultCommunityComponents",
)
