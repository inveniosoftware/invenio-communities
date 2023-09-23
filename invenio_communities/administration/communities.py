# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration OAI-PMH view module."""
from functools import partial

from flask import current_app
from invenio_administration.views.base import (
    AdminResourceDetailView,
    AdminResourceListView,
)
from invenio_search_ui.searchconfig import search_app_config

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
        "slug": {"text": "Slug", "order": 1, "width": 1},
        "metadata.title": {"text": "Title", "order": 2, "width": 4},
        # This field is for display only, it won't work on forms
        "ui.type.title_l10n": {"text": "Type", "order": 3, "width": 2},
        "featured": {"text": "Featured", "order": 4, "width": 1},
        "created": {"text": "Created", "order": 5, "width": 2},
    }

    actions = {
        "featured": {
            "text": "Feature",
            "payload_schema": CommunityFeaturedSchema,
            "order": 1,
        },
        # custom components in the UI
        "delete": {
            "text": "Delete",
            "payload_schema": None,
            "order": 2,
        },
        # custom components in the UI
        "restore": {
            "text": "Restore",
            "payload_schema": None,
            "order": 2,
        },
    }
    search_config_name = "COMMUNITIES_SEARCH"
    search_facets_config_name = "COMMUNITIES_FACETS"
    search_sort_config_name = "COMMUNITIES_SORT_OPTIONS"

    def init_search_config(self):
        """Build search view config."""
        return partial(
            search_app_config,
            config_name=self.get_search_app_name(),
            available_facets=current_app.config.get(self.search_facets_config_name),
            sort_options=current_app.config[self.search_sort_config_name],
            endpoint=self.get_api_endpoint(),
            headers=self.get_search_request_headers(),
            initial_filters=[["status", "P"]],
            hidden_params=[
                ["include_deleted", "1"],
            ],
            page=1,
            size=30,
        )

    @staticmethod
    def disabled():
        """Disable the view on demand."""
        return current_app.config["COMMUNITIES_ADMINISTRATION_DISABLED"]


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
