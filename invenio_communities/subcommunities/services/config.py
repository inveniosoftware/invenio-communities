# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Configurations for subcommunities service."""

from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    Disable,
    SystemProcess,
)
from invenio_records_permissions.policies import BasePermissionPolicy
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfig,
    ServiceConfig,
)
from invenio_requests.services.requests.config import RequestItem

from invenio_communities.generators import CommunityOwners
from invenio_communities.subcommunities.services.request import SubCommunityRequest

from .schema import SubcommunityRequestSchema


class SubCommunityPermissionPolicy(BasePermissionPolicy):
    can_request_join = [CommunityOwners()]
    can_read = [SystemProcess()]
    can_create = [Disable()]  # create is not supported
    can_search = [Disable()]  # search is not supported
    can_update = [Disable()]  # update is not supported
    can_delete = [Disable()]  # delete is not supported


class SubCommunityServiceConfig(ServiceConfig, ConfiguratorMixin):
    """SubCommunity service configuration."""

    service_id = "subcommunities"
    permission_policy_cls = SubCommunityPermissionPolicy
    result_item_cls = RequestItem
    result_list_cls = None  # TODO

    schema = FromConfig("COMMUNITIES_SUB_SERVICE_SCHEMA", SubcommunityRequestSchema)

    request_cls = FromConfig("COMMUNITIES_SUB_REQUEST_CLS", SubCommunityRequest)
