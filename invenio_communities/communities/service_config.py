# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Communities Service config."""

from flask_babelex import gettext as _
from invenio_indexer.api import RecordIndexer

from invenio_records_resources.services.records.config import ServiceConfig
from invenio_records_resources.services.records.params import FacetsParam, \
    PaginationParam, QueryParser, QueryStrParam, SortParam
from invenio_records_resources.services.records.results import RecordItem
from invenio_search import RecordsSearchV2

from invenio_communities.communities.records.api import CommunityBase

from .components import DataComponent, MetadataComponent
from .links import CommunityLink, pagination_links
from .permissions import CommunityPermissionPolicy
from .results import CommunityItem, CommunityList
from .schema import CommunitySchema


class SearchOptions:
    """Search options."""

    search_cls = RecordsSearchV2
    query_parser_cls = QueryParser
    sort_default = 'bestmatch'
    sort_default_no_query = 'bestmatch'
    sort_options = {
        "bestmatch": dict(
            title=_('Best match'),
            fields=['_score'],  # ES defaults to desc on `_score` field
        ),
        # "newest": dict(
        #     title=_('Newest'),
        #     fields=['-_created'],
        # ),
        # "oldest": dict(
        #     title=_('Oldest'),
        #     fields=['_created'],
        # ),
    }
    facets_options = dict(
        aggs={},
        post_filters={}
    )
    pagination_options = {
        "default_results_per_page": 25,
        "default_max_results": 10000
    }
    params_interpreters_cls = [
        QueryStrParam,
        PaginationParam,
        SortParam,
        FacetsParam
    ]


class CommunityServiceConfig(ServiceConfig):
    """Communities service configuration."""

    # Common configuration
    permission_policy_cls = CommunityPermissionPolicy
    # TODO
    result_item_cls = CommunityItem
    result_list_cls = CommunityList

    # Record specific configuration
    record_cls = CommunityBase
    indexer_cls = RecordIndexer
    index_dumper = None  # use default dumper defined on record class

    # Search configuration
    search = SearchOptions

    # Service schema
    schema = CommunitySchema

    links_item = {
        "self": CommunityLink("{+api}/communities/{id}"),
    }

    links_search = pagination_links("{+api}/communities{?args*}")

    # Service components
    components = [
        MetadataComponent,
        DataComponent
    ]

    community_links_list = {
        "self": CommunityLink("{+api}/communities/{id}"),
    }

    community_links_item = {
        "self": CommunityLink("{+api}/communities/{id}"),
    }
