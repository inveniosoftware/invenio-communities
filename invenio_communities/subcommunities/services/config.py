# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Configurations for subcommunities service."""

from invenio_records_permissions.generators import Disable, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfig,
    ServiceConfig,
)
from invenio_records_resources.services.records.results import RecordItem

from invenio_communities.generators import CommunityOwners
from invenio_communities.subcommunities.services.request import SubCommunityRequest

from .schema import SubcommunityRequestSchema


class SubCommunityPermissionPolicy(BasePermissionPolicy):
    """Configure permission policy for subcommunities."""

    can_request_join = [CommunityOwners()]
    can_read = [SystemProcess()]

    # Not supported actions
    can_create = [Disable()]
    can_search = [Disable()]
    can_update = [Disable()]
    can_delete = [Disable()]


class SubCommunityServiceConfig(ServiceConfig, ConfiguratorMixin):
    """SubCommunity service configuration."""

    service_id = "subcommunities"
    permission_policy_cls = SubCommunityPermissionPolicy
    result_item_cls = RecordItem
    result_list_cls = None  # TODO

    schema = FromConfig("COMMUNITIES_SUB_SERVICE_SCHEMA", SubcommunityRequestSchema)

    request_cls = FromConfig("COMMUNITIES_SUB_REQUEST_CLS", SubCommunityRequest)

    # links configuration
    links_item = {
        # TODO: add links
    }
