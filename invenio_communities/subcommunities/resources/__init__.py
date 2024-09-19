# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunity resource."""

from .config import SubCommunityResourceConfig
from .resource import SubCommunityResource

__all__ = ("SubCommunityResource", "SubCommunityResourceConfig")
