# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# invenio-administration is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration OAI-PMH view module."""
from invenio_administration.views.base import AdminResourceListView,\
    AdminResourceEditView

from invenio_communities.communities.schema import CommunityFeaturedSchema


class CommunityListView(AdminResourceListView):

    api_endpoint = "/communities"
    search_request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}
    name = "Communities"
    resource_config = "communities_resource"
    title = "Communities"
    category = "Communities"
    pid_path = "pid"

    display_search = True
    display_delete = False

    item_field_list = {
        "id": {
          "text": "ID",
          "order": 1
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
        # "featured": {
        #     "text": "Featured",
        #     "order": 4
        # },
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
