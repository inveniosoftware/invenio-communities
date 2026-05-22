# SPDX-FileCopyrightText: 2016-2021 CERN.
# SPDX-License-Identifier: MIT

"""Community views."""

from .config import CommunityResourceConfig
from .resource import CommunityResource

__all__ = (
    "CommunityResource",
    "CommunityResourceConfig",
)
