# SPDX-FileCopyrightText: 2016-2026 CERN.
# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 Northwestern University.
# SPDX-FileCopyrightText: 2026 TU Wien.
# SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""Invenio digital library framework."""

from .ext import InvenioCommunities
from .proxies import current_communities

__version__ = "29.4.0"

__all__ = ("InvenioCommunities", "current_communities")
