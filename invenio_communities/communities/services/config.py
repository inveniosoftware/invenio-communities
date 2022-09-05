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
from invenio_records_resources.services.base import Link
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

from invenio_communities.communities.records.api import Community
from invenio_communities.communities.services import facets
from invenio_communities.communities.services.results import CommunityFeaturedList, \
    CommunityItem, CommunityListResult
from .links import CommunityLink

from ...permissions import CommunityPermissionPolicy
from ..schema import CommunityFeaturedSchema, CommunitySchema
from .components import (
    CommunityAccessComponent,
    FeaturedCommunityComponent,
    OAISetComponent,
    OwnershipComponent,
    PIDComponent,
)


def _is_action_available(community, context):
    """Check if the given action is available on the request."""
    action = context.get("action")
    identity = context.get("identity")
    permission_policy_cls = context.get("permission_policy_cls")
    permission = permission_policy_cls(action, community=community)
    return permission.allows(identity)


class SearchOptions(SearchOptionsBase):
    """Search options."""

    sort_options = {
        **SearchOptionsBase.sort_options,
        "featured": dict(
            title=_("Featured"),
            fields=[
                {
                    "featured.past": {
                        "order": "desc",
                    }
                }
            ],
        ),
    }

    facets = {"type": facets.type, "visibility": facets.visibility}


class CommunityServiceConfig(RecordServiceConfig):
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
    search = SearchOptions

    # Service schema
    schema = CommunitySchema
    schema_featured = CommunityFeaturedSchema

    result_list_cls_featured = CommunityFeaturedList

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

    action_link = CommunityLink("{+api}/communities/{id}/{action_name}",
                                when=_is_action_available)

    links_search = pagination_links("{+api}/communities{?args*}")
    links_featured_search = pagination_links("{+api}/communities/featured{?args*}")
    links_user_search = pagination_links("{+api}/user/communities{?args*}")
    links_community_requests_search = pagination_links(
        "{+api}/communities/{community_id}/requests{?args*}"
    )

    available_actions = [("featured_create", "featured")]

    # Service components
    components = [
        MetadataComponent,
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
