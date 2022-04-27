# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Service API config."""

from invenio_records_resources.services import FileServiceConfig
from invenio_records_resources.services.files.links import FileLink
from invenio_records_resources.services.records.components import \
    MetadataComponent
from invenio_records_resources.services.records.config import \
    RecordServiceConfig
from invenio_records_resources.services.records.config import \
    SearchOptions as SearchOptionsBase
from invenio_records_resources.services.records.links import RecordLink, \
    pagination_links

from invenio_communities.communities.records.api import Community
from invenio_communities.communities.services import facets
from invenio_communities.communities.services.results import CommunityFeaturedList

from ...permissions import CommunityPermissionPolicy
from ..schema import CommunityFeaturedSchema, CommunitySchema
from .components import CommunityAccessComponent, FeaturedCommunityComponent, OAISetComponent, \
    OwnershipComponent, PIDComponent

from flask_babelex import lazy_gettext as _


class SearchOptions(SearchOptionsBase):
    """Search options."""

    sort_options = {
        **SearchOptionsBase.sort_options,
        "featured": dict(
            title=_('Featured'),
            fields=[{"featured.past" : {"order" : "desc",}}],
        ),
    }

    facets = {
        'type': facets.type,
        'visibility': facets.visibility
    }


class CommunityMembersLink(RecordLink):
    """Link variables setter for Community Members links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update({"community_uuid": record.id})


class CommunityServiceConfig(RecordServiceConfig):
    """Communities service configuration."""
    service_id="communities"

    # Common configuration
    permission_policy_cls = CommunityPermissionPolicy

    # Record specific configuration
    record_cls = Community
    indexer_queue_name = "communities"

    # Search configuration
    search = SearchOptions

    # Service schema
    schema = CommunitySchema
    schema_featured = CommunityFeaturedSchema

    result_list_cls_featured = CommunityFeaturedList

    links_item = {
        "self": RecordLink("{+api}/communities/{id}"),
        "self_html": RecordLink("{+ui}/communities/{id}"),
        "settings_html": RecordLink("{+ui}/communities/{id}/settings"),
        "logo": RecordLink("{+api}/communities/{id}/logo"),
        "rename": RecordLink("{+api}/communities/{id}/rename"),
        "members": CommunityMembersLink("{+api}/communities/{community_uuid}/members"),
        "public_members": CommunityMembersLink("{+api}/communities/{community_uuid}/members/public"),
        "invitations": CommunityMembersLink("{+api}/communities/{community_uuid}/invitations")
    }

    links_search = pagination_links("{+api}/communities{?args*}")
    links_user_search = pagination_links("{+api}/user/communities{?args*}")

    # Service components
    components = [
        MetadataComponent,
        PIDComponent,
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
