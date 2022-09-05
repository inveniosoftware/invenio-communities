# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# invenio-administration is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration OAI-PMH view module."""
from invenio_administration.views.base import AdminResourceListView, \
    AdminResourceEditView

from invenio_communities.communities.schema import CommunityFeaturedSchema


class CommunityListView(AdminResourceListView):

    api_endpoint = "/communities"
    name = "communities"
    resource_config = "communities_resource"
    search_request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}
    title = "Communities"
    menu_label = "Communities"
    category = "Communities"
    pid_path = "id"
    icon = "users"

    display_search = True
    display_delete = True
    display_create = False
    display_edit = True

    item_field_list = {
        "slug": {
            "text": "Slug",
            "order": 1,
        },
        "metadata.title": {
            "text": "Title",
            "order": 2
        },
        # This field is for display only, it won't work on forms
        "ui.type.title_l10n": {
            "text": "Type",
            "order": 3
        },
        "featured.past": {
            "text": "Featured",
            "order": 4
        },
        # "created": {
        #     "text": "Created",
        #     "order": 5
        # }
    }

    actions = {
        "featured_create": {
            "text": "Feature",
            "payload_schema": CommunityFeaturedSchema,
            "order": 1
        }
    }
    search_config_name = "COMMUNITIES_SEARCH"
    search_facets_config_name = "COMMUNITIES_FACETS"
    search_sort_config_name = "COMMUNITIES_SORT_OPTIONS"


class CommunityEditView(AdminResourceEditView):
    name = "communities_edit"
    url = "/communities/<pid_value>/edit"
    resource_config = "communities_resource"
    pid_path = "id"
    api_endpoint = "/communities"
    title = "Edit community"
    icon = "users"

    list_view_name = "communities"

    form_fields = {
        "metadata": {"order": 0},
        "metadata.title": {"order": 1},
        "metadata.description": {"order": 2},
        "metadata.type": {"order": 3}
    }
