# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Result items for OAI-PMH services."""

from invenio_records_resources.pagination import Pagination
from invenio_records_resources.services.base.results import ServiceListResult


# TODO: Move to invenio-records-resources together with OAISetList in
#       invenio-rdm-records and import from there
class BaseServiceListResult(ServiceListResult):
    """List of result items."""

    def __init__(
        self,
        service,
        identity,
        results,
        params=None,
        links_tpl=None,
        links_item_tpl=None,
        schema=None,
    ):
        """Constructor.

        :params service: a service instance
        :params identity: an identity that performed the service request
        :params results: the db search results
        :params params: dictionary of the query parameters
        """
        self._identity = identity
        self._results = results
        self._service = service
        self._schema = schema or service.schema
        self._params = params
        self._links_tpl = links_tpl
        self._links_item_tpl = links_item_tpl

    def __len__(self):
        """Return the total numer of hits."""
        return self.total

    def __iter__(self):
        """Iterator over the hits."""
        return self.hits

    @property
    def total(self):
        """Get total number of hits."""
        return self._results.total

    @property
    def hits(self):
        """Iterator over the hits."""
        for hit in self._results.items:
            # Project the record
            projection = self._schema.dump(
                hit,
                context=dict(
                    identity=self._identity,
                ),
            )
            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(hit)

            yield projection

    @property
    def pagination(self):
        """Create a pagination object."""
        return Pagination(
            self._params["size"],
            self._params["page"],
            self.total,
        )

    def to_dict(self):
        """Return result as a dictionary."""
        # TODO: This part should imitate the result item above. I.e. add a
        # "data" property which uses a ServiceSchema to dump the entire object.

        res = {
            "hits": {
                "hits": list(self.hits),
                "total": self.total,
            }
        }

        if self._params:
            if self._links_tpl:
                res["links"] = self._links_tpl.expand(self.pagination)

        return res


class CommunityFeaturedList(BaseServiceListResult):
    """List of featured community entry result items."""
