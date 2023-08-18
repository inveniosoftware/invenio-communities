# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Communities user moderation."""

from .actions import on_block, on_restore

__all__ = ("on_block", "on_restore")
