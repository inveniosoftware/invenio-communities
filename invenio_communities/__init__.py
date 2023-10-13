# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio digital library framework."""

from .ext import InvenioCommunities
from .proxies import current_communities

__version__ = "7.15.2"

__all__ = ("InvenioCommunities", "current_communities")
