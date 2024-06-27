# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunities service errors."""


class SubCommunityError(Exception):
    """Base error for subcommunities service."""


class ParentChildrenNotAllowed(SubCommunityError):
    """Parent community does not accept subcommunities."""
