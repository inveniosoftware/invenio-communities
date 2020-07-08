# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all

from .permissions import allow_community_owner, allow_logged_in
from .utils import comid_url_converter

#: Records REST API endpoints.
COMMUNITIES_REST_ENDPOINTS = dict(
    comid=dict(
        pid_type='comid',
        pid_minter='comid',
        pid_fetcher='comid',
        list_route='/communities/',
        item_route='/communities/<{}:pid_value>'.format(comid_url_converter),
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
        create_permission_factory_imp=allow_logged_in,
        list_permission_factory_imp=allow_all,
        update_permission_factory_imp=allow_community_owner,
        delete_permission_factory_imp=allow_community_owner,
    ),
)

COMMUNITIES_REST_FACETS = dict(
    communities=dict(
        aggs=dict(
            type=dict(
                terms=dict(field="type"),
            ),
            domain=dict(
                terms=dict(field="domains"),
            )
        ),
        post_filters=dict(
            type=terms_filter('type'),
            domain=terms_filter('domains'),
        )
    )
)

COMMUNITIES_MEMBERSHIP_REQUESTS_CONFIRMLINK_EXPIRES_IN = 1000000

SUPPORT_EMAIL = 'test@email.org'

COMMUNITIES_RECORD_INDEX = 'records-record-v1.0.0'

# TODO: Use vocabulary-based model
COMMUNITIES_DOMAINS = [
    {'text': 'Agricultural and Veterinary Sciences', 'value': 'agricultural_and_veterinary_sciences'},
    {'text': 'Biological Sciences', 'value': 'biological_sciences'},
    {'text': 'Built Environment and Design', 'value': 'built_environment_and_design'},
    {'text': 'Chemical Sciences', 'value': 'chemical_sciences'},
    {'text': 'Commerce, Management, Tourism and Services', 'value': 'commerce_management_tourism_and_services'},
    {'text': 'Earth Sciences', 'value': 'earth_sciences'},
    {'text': 'Environmental Sciences', 'value': 'environmental_sciences'},
    {'text': 'Economics', 'value': 'economics'},
    {'text': 'Education', 'value': 'education'},
    {'text': 'Engineering', 'value': 'engineering'},
    {'text': 'Technology', 'value': 'technology'},
    {'text': 'History and Archaeology', 'value': 'history_and_archaeology'},
    {'text': 'Information and Computing Sciences', 'value': 'information_and_computing_sciences'},
    {'text': 'Language, Communication and Culture', 'value': 'language_communication_and_culture'},
    {'text': 'Law and Legal Studies', 'value': 'law_and_legal_studies'},
    {'text': 'Mathematical Sciences', 'value': 'mathematical_sciences'},
    {'text': 'Medical and Health Sciences', 'value': 'medical_and_health_sciences'},
    {'text': 'Philosophy and Religious Studies', 'value': 'philosophy_and_religious_studies'},
    {'text': 'Physical Sciences', 'value': 'physical_sciences'},
    {'text': 'Psychology and Cognitive Sciences', 'value': 'psychology_and_cognitive_sciences'},
    {'text': 'Studies in Creative Arts and Writing', 'value': 'studies_in_creative_arts_and_writing'},
    {'text': 'Studies in Human Society', 'value': 'studies_in_human_society'},
]
