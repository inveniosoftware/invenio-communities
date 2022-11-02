# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Service API config."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services import FileServiceConfig
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfigSearchOptions,
    SearchOptionsMixin,
)
from invenio_records_resources.services.files.links import FileLink
from invenio_records_resources.services.records.components import (
    MetadataComponent,
    RelationsComponent,
)
from invenio_records_resources.services.records.config import RecordServiceConfig
from invenio_records_resources.services.records.config import (
    SearchOptions as SearchOptionsBase,
)
from invenio_records_resources.services.records.links import pagination_links
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
from ..schema import CommunityFeaturedSchema, CommunitySchema
from .components import (
    CommunityAccessComponent,
    CustomFieldsComponent,
    FeaturedCommunityComponent,
    OAISetComponent,
    OwnershipComponent,
    PIDComponent,
)
from .links import CommunityLink
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
    ]


class CommunityServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Communities service configuration."""

    service_id = "communities"

    # Common configuration
    permission_policy_cls = CommunityPermissionPolicy

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

    result_list_cls_featured = CommunityFeaturedList
    result_item_cls_featured = FeaturedCommunityItem

    links_item = {
        "self": CommunityLink("{+api}/communities/{id}"),
        "self_html": CommunityLink("{+ui}/communities/{slug}"),
        "settings_html": CommunityLink("{+ui}/communities/{slug}/settings"),
        "logo": CommunityLink("{+api}/communities/{id}/logo"),
        "rename": CommunityLink("{+api}/communities/{id}/rename"),
        "members": CommunityLink("{+api}/communities/{id}/members"),
        "public_members": CommunityLink("{+api}/communities/{id}/members/public"),
        "invitations": CommunityLink("{+api}/communities/{id}/invitations"),
        "requests": CommunityLink("{+api}/communities/{id}/requests"),
    }

    action_link = CommunityLink(
        "{+api}/communities/{id}/{action_name}", when=can_perform_action
    )

    links_search = pagination_links("{+api}/communities{?args*}")
    links_featured_search = pagination_links("{+api}/communities/featured{?args*}")
    links_user_search = pagination_links("{+api}/user/communities{?args*}")
    links_community_requests_search = pagination_links(
        "{+api}/communities/{community_id}/requests{?args*}"
    )

    available_actions = [
        {"action_name": "featured", "action_permission": "featured_create"}
    ]

    # Service components
    components = [
        MetadataComponent,
        CustomFieldsComponent,
        PIDComponent,
        RelationsComponent,
        CommunityAccessComponent,
        OwnershipComponent,
        FeaturedCommunityComponent,
        OAISetComponent,
    ]


class CommunityFileServiceConfig(FileServiceConfig):
    """Configuration for community files."""

    record_cls = Community
    permission_policy_cls = CommunityPermissionPolicy

    file_links_item = {
        "self": FileLink("{+api}/communities/{id}/logo"),
    }
