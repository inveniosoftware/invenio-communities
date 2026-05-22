# SPDX-FileCopyrightText: 2022 Northwestern University.
# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Members Errors."""

from ..errors import CommunityError


class AlreadyMemberError(CommunityError):
    """Exception raised when entity is already a member or already invited."""


class InvalidMemberError(CommunityError):
    """Error raised when a member is invalid.

    For instance a user/group cannot be found, or is not allowed to be added.
    """
