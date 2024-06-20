# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Sort parameter interpreter API."""

from flask import current_app
from invenio_records_resources.services.records.params.sort import SortParam


class CommunitiesSortParam(SortParam):
    """Evaluate the 'sort' parameter."""

    def apply(self, identity, search, params):
        """Evaluate the sort parameter on the search.

        If sort is set to 'featured' then use the `config.sort_featured` property
        to bypass the sort options mechanism. This is done as the `featured` option
        is set internally in the service layer.

        If `COMMUNITIES_SEARCH_SORT_BY_VERIFIED` is set, then show first the verified
        communities.
        """
        if "featured" in params.get("sort", {}):
            return search.sort(*self.config.sort_featured["fields"])

        if current_app.config["COMMUNITIES_SEARCH_SORT_BY_VERIFIED"]:
            fields = self._compute_sort_fields(params)
            return search.sort(*["-is_verified", *fields])

        return super(CommunitiesSortParam, self).apply(identity, search, params)
