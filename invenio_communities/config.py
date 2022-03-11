# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from invenio_communities.communities.services import facets
from flask_babelex import lazy_gettext as _

COMMUNITIES_ROUTES = {
    'frontpage': '/communities',
    'search': '/communities/search',
    'new': '/communities/new',
    'details': '/communities/<pid_value>',
    'settings': '/communities/<pid_value>/settings',
    'requests': '/communities/<pid_value>/requests',
    'settings_privileges': '/communities/<pid_value>/settings/privileges',
    'members': '/communities/<pid_value>/members',
    'invitations': '/communities/<pid_value>/invitations',
}
"""Communities ui endpoints."""

COMMUNITIES_ENABLED = True
"""Config to enable/disable communities blueprints."""

COMMUNITIES_FACETS = {
    'type': {
        'facet': facets.type,
        'ui': {
            'field': 'type',
        }
    },
    'visibility': {
        'facet': facets.visibility,
        'ui': {
            'field': 'visibility',
        }
    }
}
"""Available facets defined for this module."""

COMMUNITIES_SORT_OPTIONS = {
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
    "version": dict(
        title=_('Version'),
        fields=['-versions.index'],
    ),
    "updated-desc": dict(
        title=_('Recently updated'),
        fields=['-updated'],
    ),
    "updated-asc": dict(
        title=_('Least recently updated'),
        fields=['updated'],
    ),
}
"""Definitions of available record sort options."""

COMMUNITIES_ROLES = {
    'reader': dict(
        title=_('Reader'),
        description=_('Can view restricted records'),
    ),
    'curator': dict(
        title=_('Curator'),
        description=_('Can edit and view restricted records'),
    ),
    'manager': dict(
        title=_('Manager'),
        description=_('Can manage members, curate records and view restricted records'),
        can_manage_roles=['manager', 'curator', 'reader'],
    ),
    'owner': dict(
        title=_('Owner'),
        description=_('Full administrative access to the entire community.'),
        can_manage_roles=['owner', 'manager', 'curator', 'reader'],
        is_owner=True
    ),
}
"""Community roles."""

COMMUNITIES_REQUESTS_SEARCH = {
    'facets': ['type', 'status'],
    'sort': ['bestmatch', 'newest', 'oldest'],
}
"""Community requests search configuration (i.e list of community requests)"""
