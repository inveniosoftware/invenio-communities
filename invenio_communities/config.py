# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
# Copyright (C) 2023 KTH Royal Institute of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from datetime import timedelta

from invenio_i18n import lazy_gettext as _

from invenio_communities.communities.records.systemfields.access import (
    RecordSubmissionPolicyEnum,
)
from invenio_communities.communities.services import facets

COMMUNITIES_ROUTES = {
    "frontpage": "/communities",
    "search": "/communities-search",
    "deprecated_search": "/communities/search",
    "new": "/communities-new",
    "deprecated_new": "/communities/new",
    "upload": "/communities/<pid_value>/upload",
    "settings": "/communities/<pid_value>/settings",
    "requests": "/communities/<pid_value>/requests",
    "subcommunities": "/communities/<pid_value>/browse/subcommunities",
    "new_subcommunity": "/communities/<pid_value>/subcommunities/new",
    "settings_privileges": "/communities/<pid_value>/settings/privileges",
    "settings_submission_policy": "/communities/<pid_value>/settings/submission-policy",
    "settings_pages": "/communities/<pid_value>/settings/pages",
    "members": "/communities/<pid_value>/members",
    "invitations": "/communities/<pid_value>/invitations",
    "about": "/communities/<pid_value>/about",
    "curation_policy": "/communities/<pid_value>/curation-policy",
}

"""Communities ui endpoints."""

COMMUNITIES_FACETS = {
    "type": {
        "facet": facets.type,
        "ui": {
            "field": "type",
        },
    },
    "visibility": {
        "facet": facets.visibility,
        "ui": {
            "field": "visibility",
        },
    },
}
"""Available facets defined for this module."""


COMMUNITIES_SUBCOMMUNITIES_FACETS = COMMUNITIES_FACETS


COMMUNITIES_SORT_OPTIONS = {
    "bestmatch": dict(
        title=_("Best match"),
        fields=["_score"],  # ES defaults to desc on `_score` field
    ),
    "newest": dict(
        title=_("Newest"),
        fields=["-created"],
    ),
    "oldest": dict(
        title=_("Oldest"),
        fields=["created"],
    ),
    "version": dict(
        title=_("Version"),
        fields=["-versions.index"],
    ),
    "updated-desc": dict(
        title=_("Recently updated"),
        fields=["-updated"],
    ),
    "updated-asc": dict(
        title=_("Least recently updated"),
        fields=["updated"],
    ),
}
"""Definitions of available record sort options."""


COMMUNITIES_ROLES = [
    dict(
        name="reader",
        title=_("Reader"),
        description=_("Can view restricted records."),
        can_view=True,
    ),
    dict(
        name="curator",
        title=_("Curator"),
        description=_("Can curate records and view restricted records."),
        can_curate=True,
        can_view=True,
    ),
    dict(
        name="manager",
        title=_("Manager"),
        description=_(
            "Can manage members, curate records " "and view restricted records."
        ),
        can_manage_roles=["manager", "curator", "reader"],
        can_manage=True,
        can_curate=True,
        can_view=True,
    ),
    dict(
        name="owner",
        title=_("Owner"),
        description=_("Full administrative access to the entire community."),
        can_manage_roles=["owner", "manager", "curator", "reader"],
        is_owner=True,
        can_manage=True,
        can_curate=True,
        can_view=True,
    ),
]
"""Community roles."""

COMMUNITIES_SEARCH = {
    "facets": ["type", "visibility"],
    "sort": ["bestmatch", "newest", "oldest"],
}
"""Community search configuration (i.e list of communities)"""

COMMUNITIES_SEARCH_SORT_BY_VERIFIED = False
"""Sort communities by 'verified' first."""

COMMUNITIES_SUBCOMMUNITIES_SEARCH = {
    "facets": ["type"],
    "sort": ["bestmatch", "newest", "oldest"],
}
"""Community search configuration (i.e list of communities)"""

COMMUNITIES_REQUESTS_SEARCH = {
    "facets": ["type", "status"],
    "sort": ["bestmatch", "newest", "oldest"],
}
"""Community requests search configuration (i.e list of community requests)"""

COMMUNITIES_MEMBERS_SEARCH = {
    "facets": ["role", "visibility"],
    "sort": ["bestmatch", "name", "newest", "oldest"],
}
"""Community requests search configuration (i.e list of community requests)"""

COMMUNITIES_MEMBERS_SORT_OPTIONS = {
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
"""Definitions of available record sort options."""

COMMUNITIES_MEMBERS_FACETS = {
    "role": {
        "facet": facets.role,
        "ui": {
            "field": "role",
        },
    },
    "visibility": {
        "facet": facets.visible,
        "ui": {
            "field": "visible",
        },
    },
}
"""Available facets defined for this module."""

COMMUNITIES_INVITATIONS_SEARCH = {
    "facets": ["type", "status"],
    "sort": ["bestmatch", "name", "newest", "oldest"],
}
"""Community invitations search configuration (i.e list of community invitations)"""

COMMUNITIES_INVITATIONS_SORT_OPTIONS = {
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
"""Definitions of available record sort options."""


COMMUNITIES_INVITATIONS_EXPIRES_IN = timedelta(days=30)
""""Default amount of time before an invitation expires."""

COMMUNITIES_LOGO_MAX_FILE_SIZE = 10**6
"""Community logo size quota, in bytes."""


COMMUNITIES_NAMESPACES = {}
"""Custom fields namespaces.

.. code-block:: python
    {<namespace>: <uri>, ...}

For example:

.. code-block:: python
    {
        "cern": "https://cern.ch/terms",
        "dwc": "http://rs.tdwg.org/dwc/terms/"
    }

"""

COMMUNITIES_CUSTOM_FIELDS = []
"""Communities custom fields definition.

Of the shape:

.. code-block:: python

    [
        <custom-field-class-type(name='field')>,
        # ...
        <custom-field-class-type(name='fieldN')>'
    ]

For example:

.. code-block:: python

    [
        TextCF(name="experiment"),
        ...
    ]
"""

COMMUNITIES_CUSTOM_FIELDS_UI = []
"""Communities custom fields UI configuration.

Of the shape:

.. code-block:: python

    [{
        section: <section_name>,
        fields: [
            {
                field: "path-to-field",  # this should be validated against the defined fields in `RDM_CUSTOM_FIELDS`
                ui_widget: "<ui-widget-name>",  # predefined or user defined ui widget
                props: {
                    label:"<ui-label-to-display>",
                    placeholder:"<placeholder-passed-to-widget>",
                    icon:"<icon-passed-to-widget>",
                    description:"<description-passed-to-widget>",
                }
            },
        ],

        # ...
    }]

For example:

.. code-block:: python

    [{
        "section": "CERN Experiment"
        "fields" : [{
            field: "experiment",  # this should be validated against the defined fields in `RDM_CUSTOM_FIELDS`
            ui_widget: "CustomTextField",  # user defined widget in my-site
            props: {
                label: "Experiment",
                placeholder: "Type an experiment...",
                icon: "pencil",
                description: "You should fill this field with one of the experiments e.g LHC, ATLAS etc.",
            }
        },
        ...
    }]
"""

COMMUNITIES_ALLOW_RESTRICTED = True

# Cache duration
# 60 seconds * 60 (1 hour) * 24 (1 day)
COMMUNITIES_IDENTITIES_CACHE_TIME = 60 * 60 * 24

# Redis URL Cache for identities
COMMUNITIES_IDENTITIES_CACHE_REDIS_URL = "redis://localhost:6379/4"

# Cache handler
COMMUNITIES_IDENTITIES_CACHE_HANDLER = (
    "invenio_communities.cache.redis:IdentityRedisCache"
)

COMMUNITIES_OAI_SETS_PREFIX = "community-"

COMMUNITIES_ALWAYS_SHOW_CREATE_LINK = False
"""Controls visibility of 'New Community' btn based on user's permission when set to True."""

COMMUNITIES_ALLOW_MEMBERSHIP_REQUESTS = False
"""Feature flag for membership request."""

COMMUNITIES_DEFAULT_RECORD_SUBMISSION_POLICY = RecordSubmissionPolicyEnum.OPEN
"""Default value of record submission policy community access setting."""
