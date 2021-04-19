# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2020 European Union.
#
# Invenio-communitys-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Communities Service API."""

from elasticsearch_dsl import Q
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.records import RecordService


class CommunityService(RecordService):
    """community Service."""

    def search_user_communities(
            self, identity, params=None, es_preference=None, **kwargs):
        """Search for records matching the querystring."""
        self.require_permission(identity, 'search_user_communities')

        # Prepare and execute the search
        params = params or {}
        search_result = self._search(
            'search',
            identity,
            params,
            es_preference,
            extra_filter=Q(
                "term",
                **{"access.owned_by.user": identity.id}
            ),
            permission_action='read',
            **kwargs).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(self.config.links_user_search, context={
                "args": params
            }),
            links_item_tpl=self.links_item_tpl,
        )
