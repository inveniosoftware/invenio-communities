# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration OAI-PMH view module."""
from invenio_administration.views.base import (
    AdminResourceDetailView,
    AdminResourceListView,
)

from invenio_communities.communities.schema import CommunityFeaturedSchema


class CommunityListView(AdminResourceListView):
    """Search admin view."""

    api_endpoint = "/communities"
    name = "communities"
    resource_config = "communities_resource"
    search_request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}
    title = "Communities"
    menu_label = "Communities"
    category = "Communities"
    pid_path = "id"
    icon = "users"
    template = "invenio_communities/administration/community_search.html"

    display_search = True
    display_delete = False
    display_create = False
    display_edit = False

    item_field_list = {
        "slug": {
            "text": "Slug",
            "order": 1,
        },
        "metadata.title": {"text": "Title", "order": 2},
        # This field is for display only, it won't work on forms
        "ui.type.title_l10n": {"text": "Type", "order": 3},
        "featured": {"text": "Featured", "order": 4},
        "created": {"text": "Created", "order": 5},
    }

    actions = {
        "featured": {
            "text": "Feature",
            "payload_schema": CommunityFeaturedSchema,
            "order": 1,
        }
    }
    search_config_name = "COMMUNITIES_SEARCH"
    search_facets_config_name = "COMMUNITIES_FACETS"
    search_sort_config_name = "COMMUNITIES_SORT_OPTIONS"


class CommunityDetailView(AdminResourceDetailView):
    """Admin community detail view."""

    url = "/communities/<pid_value>"
    api_endpoint = "/communities"
    name = "community-details"
    resource_config = "communities_resource"
    title = "Community"

    template = "invenio_communities/administration/community_details.html"
    display_delete = False
    display_edit = False

    list_view_name = "communities"
    pid_path = "id"
    request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}

    actions = {
        "featured": {
            "text": "Feature",
            "payload_schema": CommunityFeaturedSchema,
            "order": 1,
        }
    }

    item_field_list = {
        "slug": {
            "text": "Slug",
            "order": 1,
        },
        "metadata.title": {"text": "Title", "order": 2},
        # This field is for display only, it won't work on forms
        "ui.type.title_l10n": {"text": "Type", "order": 3},
        "created": {"text": "Created", "order": 5},
    }
