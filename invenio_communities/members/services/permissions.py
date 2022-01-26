# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Permission Policy."""

from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy


class CommunityMembersPermissionPolicy(BasePermissionPolicy):
    """Permissions for Community Members CRUD operations."""

    # TODO #384
    can_read = [AnyUser()]

    can_search = [AnyUser(), SystemProcess()]
