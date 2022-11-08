# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-App-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration helper for React-SearchKit."""

from functools import partial

from flask import current_app
from invenio_search_ui.searchconfig import search_app_config


def search_app_context():
    """Search app context processor."""
    return {
        "search_app_communities_config": partial(
            search_app_config,
            config_name="COMMUNITIES_SEARCH",
            available_facets=current_app.config["COMMUNITIES_FACETS"],
            sort_options=current_app.config["COMMUNITIES_SORT_OPTIONS"],
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
            endpoint="/api/communities",
        ),
        "search_app_communities_requests_config": partial(
            search_app_config,
            config_name="COMMUNITIES_REQUESTS_SEARCH",
            available_facets=current_app.config["REQUESTS_FACETS"],
            sort_options=current_app.config["COMMUNITIES_SORT_OPTIONS"],
            headers={"Accept": "application/json"},
            initial_filters=[["is_open", "true"]],
            endpoint="/api/requests",
            hidden_params=[["expand", "1"]],
        ),
        "search_app_communities_members_config": partial(
            search_app_config,
            config_name="COMMUNITIES_MEMBERS_SEARCH",
            available_facets=current_app.config["COMMUNITIES_MEMBERS_FACETS"],
            sort_options=current_app.config["COMMUNITIES_MEMBERS_SORT_OPTIONS"],
            headers={"Accept": "application/json"},
            default_size=25,
            pagination_options=(25, 50, 75),
        ),
        "search_app_communities_invitations_config": partial(
            search_app_config,
            config_name="COMMUNITIES_INVITATIONS_SEARCH",
            available_facets=current_app.config["REQUESTS_FACETS"],
            sort_options=current_app.config["COMMUNITIES_INVITATIONS_SORT_OPTIONS"],
            headers={"Accept": "application/json"},
            initial_filters=[["is_open", "true"]],
            endpoint="/api/requests",
        ),
    }
