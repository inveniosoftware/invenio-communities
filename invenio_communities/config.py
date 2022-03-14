# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
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
    'settings_privileges': '/communities/<pid_value>/settings/privileges',
    'members': '/communities/<pid_value>/members',
    'invitations': '/communities/<pid_value>/invitations'
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
        can_manage_members=['manager', 'curator', 'reader'],
    ),
    'owner': dict(
        title=_('Owner'),
        description=_('Full administrative access to the entire community.'),
        can_manage_members=['owner', 'manager', 'curator', 'reader'],
        is_owner=True
    ),
}
"""Community roles."""
