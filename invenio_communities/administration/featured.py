# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# invenio-administration is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration OAI-PMH view module."""
from invenio_administration.views.base import AdminResourceListView

from invenio_communities.communities.schema import CommunityFeaturedSchema


class FeaturedCommunityListView(AdminResourceListView):

    api_endpoint = "/communities/featured"
    search_request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}
    name = "featured_communities"
    resource_config = "communities_resource"
    title = "Featured communities"
    category = "Communities"
    pid_path = "id"
    menu_label = "Featured"
    icon = "star_outline"

    display_search = True
    display_delete = True

    item_field_list = {
        "slug": {
          "text": "ID",
          "order": 1
        },
        "metadata.title": {
            "text": "Title",
            "order": 2
        },
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

    search_config_name = "COMMUNITIES_SEARCH"
    search_facets_config_name = "COMMUNITIES_FACETS"
    search_sort_config_name = "COMMUNITIES_SORT_OPTIONS"

    @classmethod
    def get_service_schema(cls):
        return CommunityFeaturedSchema()

