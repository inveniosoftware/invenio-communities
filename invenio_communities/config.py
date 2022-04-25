# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from datetime import timedelta

from flask_babelex import lazy_gettext as _

from invenio_communities.communities.services import facets

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

COMMUNITIES_ALLOW_GROUP_INVITES = True
"""Config to allow invitation of groups."""

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


COMMUNITIES_ROLES = [
    dict(
        name="reader",
        title=_('Reader'),
        description=_('Can view restricted records'),
    ),
    dict(
        name="curator",
        title=_('Curator'),
        description=_('Can edit and view restricted records'),
    ),
    dict(
        name="manager",
        title=_('Manager'),
        description=_('Can manage members, curate records '
                      'and view restricted records'),
        can_manage_roles=['manager', 'curator', 'reader'],
        can_manage=True
    ),
    dict(
        name="owner",
        title=_('Owner'),
        description=_('Full administrative access to the entire community.'),
        can_manage_roles=['owner', 'manager', 'curator', 'reader'],
        is_owner=True,
        can_manage=True
    ),
]
"""Community roles."""

COMMUNITIES_SEARCH = {
    'facets': ['type'],
    'sort': ['bestmatch', 'newest', 'oldest'],
}
"""Community search configuration (i.e list of communities)"""

COMMUNITIES_REQUESTS_SEARCH = {
    'facets': ['type', 'status'],
    'sort': ['bestmatch', 'newest', 'oldest'],
}
"""Community requests search configuration (i.e list of community requests)"""

COMMUNITIES_MEMBERS_SEARCH = {
    'facets': ['role', 'visibility'],
    'sort': ['bestmatch', 'newest', 'oldest'],
}
"""Community requests search configuration (i.e list of community requests)"""

COMMUNITIES_MEMBERS_FACETS = {
    'role': {
        'facet': facets.role,
        'ui': {
            'field': 'role',
        }
    },
    'visibility': {
        'facet': facets.visible,
        'ui': {
            'field': 'visible',
        }
    }
}
"""Available facets defined for this module."""

COMMUNITIES_INVITATIONS_SEARCH = {
    'facets': ['type', 'status'],
    'sort': ['bestmatch', 'newest', 'oldest'],
}
"""Community invitations search configuration (i.e list of community invitations)"""

COMMUNITIES_INVITATIONS_SORT_OPTIONS = {
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
"""Definitions of available record sort options."""


COMMUNITIES_INVITATIONS_EXPIRES_IN = timedelta(days=30)
""""Default amount of time before an invitation expires."""
