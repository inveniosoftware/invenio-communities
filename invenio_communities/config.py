# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

COMMUNITIES_MEMBERSHIP_REQUESTS_CONFIRMLINK_EXPIRES_IN = 1000000

SUPPORT_EMAIL = 'test@email.org'

COMMUNITIES_RECORD_INDEX = 'records'

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

COMMUNITIES_ROUTES = {
    'frontpage': '/communities',
    'search': '/communities/search',
    'new': '/communities/new',
    'details': '/communities/<pid_value>',
    'settings': '/communities/<pid_value>/settings',
    'settings_privileges': '/communities/<pid_value>/settings/privileges',
}
"""Communities ui endpoints."""

COMMUNITIES_ENABLED = True
"""Config to enable/disable communities blueprints."""
