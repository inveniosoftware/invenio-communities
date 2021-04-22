# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Community views."""

from .config import CommunityFileServiceConfig, CommunityServiceConfig, \
    SearchOptions
from .service import CommunityService

__all__ = (
    'CommunityService',
    'CommunityServiceConfig',
    'CommunityFileServiceConfig',
    'SearchOptions',
)
