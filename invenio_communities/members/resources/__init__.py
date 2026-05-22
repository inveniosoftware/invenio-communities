# SPDX-FileCopyrightText: 2016-2021 CERN.
# SPDX-License-Identifier: MIT

"""Member views."""

from .config import MemberResourceConfig
from .resource import MemberResource

__all__ = (
    "MemberResource",
    "MemberResourceConfig",
)
