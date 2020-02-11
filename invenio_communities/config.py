# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

from invenio_records_rest.utils import allow_all
from invenio_records_rest.facets import terms_filter

#: Records REST API endpoints.
COMMUNITIES_REST_ENDPOINTS = dict(
    comid=dict(
        pid_type='comid',
        pid_minter='comid',
        pid_fetcher='comid',
        list_route='/communities/',
        item_route='/communities/<{0}:pid_value>'.format(
            'pid(comid,record_class="invenio_communities.api:Community",'
            'object_type="com")'
        ),
        search_index='communities',
        record_class='invenio_communities.api:Community',
        record_serializers={
            'application/json': (
                'invenio_communities.serializers.json_v1_response'),
        },
        search_serializers={
            'application/json': (
                'invenio_communities.serializers:json_v1_search'),
        },
        record_loaders={
            'application/json': ('invenio_communities.loaders:json_v1'),
        },
        indexer_class='invenio_communities.indexer:CommunityIndexer',
        default_media_type='application/json',
        read_permission_factory_imp=allow_all,
        create_permission_factory_imp=allow_all,
        list_permission_factory_imp=allow_all,
        update_permission_factory_imp=allow_all,
        delete_permission_factory_imp=allow_all
    ),
)

COMMUNITIES_MEMBERSHIP_REQUESTS_CONFIRMLINK_EXPIRES_IN = 1000000

SUPPORT_EMAIL = 'test@email.org'


COMMUNITIES_REST_FACETS = dict(
    communities=dict(
        aggs=dict(
            type=dict(
                terms=dict(field="type"),
            ),
            domain=dict(
                terms=dict(field="domain"),
            )
        ),
        post_filters=dict(
            access_right=terms_filter('access_right'),
            file_type=terms_filter('filetype'),
        )
    )
)
