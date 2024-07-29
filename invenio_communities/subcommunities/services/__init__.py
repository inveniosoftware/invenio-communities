# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunities module service."""

from .config import SubCommunityServiceConfig
from .service import SubCommunityService

__all__ = ("SubCommunityService", "SubCommunityServiceConfig")
