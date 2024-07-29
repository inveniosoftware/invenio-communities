# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Errors."""

from ..errors import CommunityError


class AlreadyMemberError(CommunityError):
    """Exception raised when entity is already a member or already invited."""


class InvalidMemberError(CommunityError):
    """Error raised when a member is invalid.

    For instance a user/group cannot be found, or is not allowed to be added.
    """
