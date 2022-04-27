# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Service Config."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services import RecordServiceConfig, \
    SearchOptions, pagination_links

from ...communities.records.api import Community
from ...permissions import CommunityPermissionPolicy
from ..records import Member
from . import facets
from .schemas import MemberEntitySchema


class PublicSearchOptions(SearchOptions):
    # TODO: should restrict fields that's being searched on.
    # query_parser_cls = QueryParser
    sort_default = 'bestmatch'
    # TODO: sort options should be by username and not expose e.g. creation
    # date
    sort_default_no_query = 'newest'
    sort_options = {
        "bestmatch": dict(
            title=_('Best match'),
            fields=['_score'],  # ES defaults to desc on `_score` field
        ),
        "newest": dict(
            title=_('Newest'),
            fields=['-created'],
        ),
    }


class InvitationsSearchOptions(SearchOptions):
    # TODO: should restrict fields that's being searched on.
    # query_parser_cls = QueryParser
    sort_default = 'bestmatch'
    # TODO: sort options should be by username and not expose e.g. creation
    # date
    sort_default_no_query = 'newest'
    sort_options = {
        "bestmatch": dict(
            title=_('Best match'),
            fields=['_score'],  # ES defaults to desc on `_score` field
        ),
        "newest": dict(
            title=_('Newest'),
            fields=['-created'],
        ),
        "oldest": dict(
            title=_('Oldest'),
            fields=['created'],
        ),
    }

    facets = {
        'role': facets.role,
        'status': facets.status,
    }


class MemberSearchOptions(PublicSearchOptions):
    """Search options."""
    sort_default = 'bestmatch'
    sort_default_no_query = 'newest'
    sort_options = {
        "bestmatch": dict(
            title=_('Best match'),
            fields=['_score'],  # ES defaults to desc on `_score` field
        ),
        # TODO add user name
        "newest": dict(
            title=_('Newest'),
            fields=['-created'],
        ),
        "oldest": dict(
            title=_('Oldest'),
            fields=['created'],
        ),
    }

    facets = {
        'role': facets.role,
        'visibility': facets.visibility,
    }


class MemberServiceConfig(RecordServiceConfig):
    """Member Service Config."""
    service_id="members"

    community_cls = Community
    record_cls = Member
    schema = MemberEntitySchema
    indexer_queue_name = "members"
    relations = {
        "users": ["user"]
    }

    permission_policy_cls = CommunityPermissionPolicy

    search = MemberSearchOptions
    search_public = PublicSearchOptions
    search_invitations = InvitationsSearchOptions

    # No links
    links_item = {}

    # ResultList configurations
    links_search = pagination_links(
        "{+api}/communities/{community_id}/members{?args*}"
    )
