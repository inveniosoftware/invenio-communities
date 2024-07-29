# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community views."""

from .components import DefaultCommunityComponents
from .config import CommunityFileServiceConfig, CommunityServiceConfig, SearchOptions
from .service import CommunityService

__all__ = (
    "CommunityService",
    "CommunityServiceConfig",
    "CommunityFileServiceConfig",
    "SearchOptions",
    "DefaultCommunityComponents",
)
