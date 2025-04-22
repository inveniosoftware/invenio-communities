# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2022-2025 Northwestern University.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Service API config."""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import FileServiceConfig
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfig,
    FromConfigSearchOptions,
    SearchOptionsMixin,
)
from invenio_records_resources.services.files.links import FileEndpointLink
from invenio_records_resources.services.records.config import (
    RecordServiceConfig,
)
from invenio_records_resources.services.records.config import (
    SearchOptions as SearchOptionsBase,
)
from invenio_records_resources.services.records.links import (
    pagination_endpoint_links,
)
from invenio_records_resources.services.records.params import (
    FacetsParam,
    PaginationParam,
    QueryStrParam,
)

from invenio_communities.communities.records.api import Community
from invenio_communities.communities.services import facets
from invenio_communities.communities.services.results import (
    CommunityFeaturedList,
    CommunityItem,
    CommunityListResult,
    FeaturedCommunityItem,
)

from ...permissions import CommunityPermissionPolicy, can_perform_action
from ..schema import CommunityFeaturedSchema, CommunitySchema, TombstoneSchema
from .components import DefaultCommunityComponents
from .links import CommunityEndpointLink, CommunityUIEndpointLink
from .search_params import IncludeDeletedCommunitiesParam, StatusParam
from .sort import CommunitiesSortParam


class SearchOptions(SearchOptionsBase, SearchOptionsMixin):
    """Search options."""

    sort_featured = {
        "title": _("Featured"),
        "fields": [
            {
                "featured.past": {
                    "order": "desc",
                }
            }
        ],
    }

    facets = {"type": facets.type, "visibility": facets.visibility}
    params_interpreters_cls = [
        QueryStrParam,
        PaginationParam,
        CommunitiesSortParam,
        FacetsParam,
        StatusParam,
        IncludeDeletedCommunitiesParam,
    ]


def children_allowed(record, _):
    """Determine if children are allowed."""
    try:
        return getattr(record.children, "allow", False)
    except AttributeError:
        # This is needed because a types.SimpleNamespace object can be passed by
        # the entity_resolver when generating the logo which does not have
        # `children` and fails
        return False


class CommunityServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Communities service configuration."""

    service_id = "communities"

    # Common configuration
    permission_policy_cls = FromConfig(
        "COMMUNITIES_PERMISSION_POLICY", default=CommunityPermissionPolicy
    )
    # Record specific configuration
    record_cls = Community
    result_item_cls = CommunityItem
    result_list_cls = CommunityListResult
    indexer_queue_name = "communities"

    # Search configuration
    search = FromConfigSearchOptions(
        "COMMUNITIES_SEARCH",
        "COMMUNITIES_SORT_OPTIONS",
        "COMMUNITIES_FACETS",
        search_option_cls=SearchOptions,
    )

    # Service schema
    schema = CommunitySchema
    schema_featured = CommunityFeaturedSchema
    schema_tombstone = TombstoneSchema

    result_list_cls_featured = CommunityFeaturedList
    result_item_cls_featured = FeaturedCommunityItem

    links_item = {
        "self": CommunityEndpointLink("communities.read", params=["pid_value"]),
        "self_html": CommunityUIEndpointLink(
            "invenio_app_rdm_communities.communities_home", params=["pid_value"]
        ),
        "settings_html": CommunityUIEndpointLink(
            "invenio_communities.communities_settings", params=["pid_value"]
        ),
        "logo": CommunityEndpointLink("communities.read_logo", params=["pid_value"]),
        "rename": CommunityEndpointLink("communities.rename", params=["pid_value"]),
        "members": CommunityEndpointLink(
            "community_members.search", params=["pid_value"]
        ),
        "public_members": CommunityEndpointLink(
            "community_members.search_public", params=["pid_value"]
        ),
        "invitations": CommunityEndpointLink(
            "community_members.invite", params=["pid_value"]
        ),
        "requests": CommunityEndpointLink(
            "communities.search_community_requests", params=["pid_value"]
        ),
        "records": CommunityEndpointLink(
            "community-records.search", params=["pid_value"]
        ),
        "subcommunities": CommunityEndpointLink(
            "communities.search_subcommunities",
            when=children_allowed,
            params=["pid_value"],
        ),
        "membership_requests": CommunityEndpointLink(
            "community_members.request_membership", params=["pid_value"]
        ),
    }

    action_link = CommunityEndpointLink(
        "communities.featured_create",  # This works because only 1 action
        when=can_perform_action,
        params=["pid_value"],
    )

    links_search = pagination_endpoint_links("communities.search")
    links_featured_search = pagination_endpoint_links(
        "communities.featured_communities_search"
    )
    links_user_search = pagination_endpoint_links("communities.search_user_communities")
    links_community_requests_search = pagination_endpoint_links(
        "communities.search_community_requests", params=["pid_value"]
    )
    links_subcommunities_search = pagination_endpoint_links(
        "communities.search_subcommunities", params=["pid_value"]
    )

    available_actions = [
        {"action_name": "featured", "action_permission": "featured_create"}
    ]

    # Service components
    components = FromConfig(
        "COMMUNITIES_SERVICE_COMPONENTS", default=DefaultCommunityComponents
    )


class CommunityFileServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Configuration for community files."""

    record_cls = Community
    permission_policy_cls = FromConfig(
        "COMMUNITIES_PERMISSION_POLICY", default=CommunityPermissionPolicy
    )
    file_links_item = {
        "self": FileEndpointLink("communities.read_logo", params=["pid_value"]),
    }
