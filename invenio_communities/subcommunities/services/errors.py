# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Subcommunities service errors."""


class SubCommunityError(Exception):
    """Base error for subcommunities service."""


class ParentChildrenNotAllowed(SubCommunityError):
    """Parent community does not accept subcommunities."""
