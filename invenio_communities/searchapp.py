# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2022 CERN.
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
        #The Following functions should be defined for the communties
        # search_app_communities_config
        # search_app_communities_records_config
        # search_app_communities_members_config
        # search_app_communities_invitations_config
        # search_app_communities_requests_config

        #For them, the following configurations should be applied, respectively
        # COMMUNITIES_SEARCH
        # COMMUNITIES_RECORDS_SEARCH
        # COMMUNITIES_MEMBERS_SEARCH
        # COMMUNITIES_INVITATIONS_SEARCH
        # COMMUNITIES_REQUESTS_SEARCH

        'search_app_communities_requests_config': partial(
            search_app_config,
            config_name = 'COMMUNITIES_REQUESTS_SEARCH',
            available_facets = current_app.config['REQUESTS_FACETS'],
            sort_options = current_app.config['COMMUNITIES_SORT_OPTIONS'],
            headers={"Accept": "application/json"},
            initial_filters=[["is_open", "true"]]
        )
    }
