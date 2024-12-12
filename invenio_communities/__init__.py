# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio digital library framework."""

from .ext import InvenioCommunities
from .proxies import current_communities

__version__ = "18.0.0.dev1"

__all__ = ("InvenioCommunities", "current_communities")
