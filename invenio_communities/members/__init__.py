# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members."""

from .errors import AlreadyMemberError, LastOwnerError, \
    ManagerSelfRoleChangeError, OwnerSelfRoleChangeError
from .records import Member, MemberModel
from .services import MemberService, MemberServiceConfig, ROLE_TYPES


__all__ = (
    'AlreadyMemberError',
    'LastOwnerError',
    'Member',
    'MemberModel',
    # 'MemberResource',
    # 'MemberResourceConfig',
    "ManagerSelfRoleChangeError",
    'MemberService',
    'MemberServiceConfig',
    "OwnerSelfRoleChangeError",
    "ROLE_TYPES",
)
