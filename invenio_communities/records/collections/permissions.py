# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community collection permissions."""

from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies import BasePermissionPolicy

from invenio_communities.permissions import CommunityOwner


class CommunityCollectionsPermissionPolicy(BasePermissionPolicy):

    can_get_collection = [AnyUser()]
    can_list_collections = [AnyUser()]
    can_create_collection = [CommunityOwner()]
    can_update_collection = [CommunityOwner()]
    can_delete_collection = [CommunityOwner()]
    can_update_record_collections = [CommunityOwner()]
    can_get_record_collections = [AnyUser()]
