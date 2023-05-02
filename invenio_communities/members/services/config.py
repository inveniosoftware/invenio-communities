# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Service Config."""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import (
    RecordServiceConfig,
    SearchOptions,
    pagination_links,
)
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig
from invenio_records_resources.services.records.components import MetadataComponent
from invenio_records_resources.services.records.queryparser import (
    QueryParser,
    SearchFieldTransformer,
)

from ...communities.records.api import Community
from ...permissions import CommunityPermissionPolicy
from ..records import Member
from ..records.api import ArchivedInvitation
from . import facets
from .components import CommunityMemberCachingComponent
from .schemas import MemberEntitySchema


class PublicSearchOptions(SearchOptions):
    """Public Search Options."""

    sort_default = "bestmatch"
    sort_default_no_query = "name"
    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # ES defaults to desc on `_score` field
        ),
        "name": dict(
            title=_("Name"),
            fields=["user.profile.full_name.keyword"],
        ),
    }

    query_parser_cls = QueryParser.factory(
        # fields serves also as a filter, since only the ones mentioned there
        # will be queried by the search engine, using multi_match query.
        fields=[
            "user.username^2",
            "user.profile.full_name^3",
            "user.profile.affiliations",
        ],
        allow_list=[  # present to restrict to mapped fields
            "user.profile.affiliations",
            "user.profile.full_name",
            "user.username",
        ],
        mapping={
            "affiliation": "user.profile.affiliations",
            "affiliations": "user.profile.affiliations",
            "full_name": "user.profile.full_name",
            "fullname": "user.profile.full_name",
            "name": "user.profile.full_name",
            "username": "user.username",
        },
        tree_transformer_cls=SearchFieldTransformer,
    )


class InvitationsSearchOptions(SearchOptions):
    """Invitations Search Options."""

    # TODO: should restrict fields that's being searched on.
    # query_parser_cls = QueryParser
    sort_default = "bestmatch"
    sort_default_no_query = "name"
    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # ES defaults to desc on `_score` field
        ),
        "name": dict(
            title=_("Name"),
            fields=["user.profile.full_name.keyword"],
        ),
        "newest": dict(
            title=_("Newest"),
            fields=["-created"],
        ),
        "oldest": dict(
            title=_("Oldest"),
            fields=["created"],
        ),
    }

    facets = {
        "role": facets.role,
        "status": facets.status,
        "is_open": facets.is_open,
    }


class MemberSearchOptions(PublicSearchOptions):
    """Search options."""

    sort_default = "bestmatch"
    sort_default_no_query = "name"
    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # ES defaults to desc on `_score` field
        ),
        "name": dict(
            title=_("Name"),
            fields=["user.profile.full_name.keyword"],
        ),
        "newest": dict(
            title=_("Newest"),
            fields=["-created"],
        ),
        "oldest": dict(
            title=_("Oldest"),
            fields=["created"],
        ),
    }

    facets = {
        "role": facets.role,
        "visibility": facets.visibility,
    }

    query_parser_cls = QueryParser.factory(
        fields=[
            "user.username^2",
            "user.email^2",
            "user.profile.full_name^3",
            "user.profile.affiliations",
        ],
        allow_list=[  # present to restrict to mapping
            "user.profile.affiliations",
            "user.profile.full_name",
            "user.username",
            "user.email",
        ],
        mapping={
            "affiliation": "user.profile.affiliations",
            "affiliations": "user.profile.affiliations",
            "email": "user.email",
            "full_name": "user.profile.full_name",
            "fullname": "user.profile.full_name",
            "name": "user.profile.full_name",
            "username": "user.username",
        },
        tree_transformer_cls=SearchFieldTransformer,
    )


class MemberServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Member Service Config."""

    service_id = "members"

    community_cls = Community
    record_cls = Member
    schema = MemberEntitySchema
    indexer_queue_name = "members"
    relations = {"users": ["user"]}

    archive_cls = ArchivedInvitation
    archive_indexer_cls = RecordServiceConfig.indexer_cls
    archive_indexer_queue_name = "archived-invitations"

    permission_policy_cls = FromConfig(
        "COMMUNITIES_PERMISSION_POLICY", default=CommunityPermissionPolicy
    )
    search = MemberSearchOptions
    search_public = PublicSearchOptions
    search_invitations = InvitationsSearchOptions

    # No links
    links_item = {}

    # ResultList configurations
    links_search = pagination_links("{+api}/communities/{community_id}/members{?args*}")

    # Service components
    components = [
        MetadataComponent,
        CommunityMemberCachingComponent,
    ]
