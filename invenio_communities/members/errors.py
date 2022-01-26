# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Errors."""


from ..errors import CommunityError


class AlreadyMemberError(CommunityError):
    """Exception raised when entity is already a member."""


class LastOwnerError(CommunityError):
    """Exception raised when entity is last owner and trying to leave."""


class OwnerSelfRoleChangeError(CommunityError):
    """Exception raised when owner tries to change their role."""


class ManagerSelfRoleChangeError(CommunityError):
    """Exception raised when manager tries to change their role."""
