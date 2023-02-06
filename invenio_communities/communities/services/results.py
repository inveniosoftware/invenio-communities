# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Result items for OAI-PMH services."""

from invenio_records_resources.services.records.results import (
    FieldsResolver,
    RecordItem,
    RecordList,
)


class CommunityListResult(RecordList):
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
        expandable_fields=None,
        expand=False,
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
        self._expand = expand

    @property
    def hits(self):
        """Iterator over the hits."""
        for hit in self._results:
            # Load dump
            record = self._service.record_cls.loads(hit.to_dict())

            # TODO better handling of featured field
            record["featured"] = True if hit.featured["past"] else False

            # Project the record
            projection = self._schema.dump(
                record,
                context=dict(
                    identity=self._identity,
                    record=record,
                ),
            )
            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    self._identity, record
                )

            yield projection


class CommunityFeaturedList(CommunityListResult):
    """List of featured community entry result items."""

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
        for record in self._results.items:
            # Project the record
            projection = self._schema.dump(
                record,
                context=dict(
                    identity=self._identity,
                    record=record,
                ),
            )
            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    self._identity, record
                )

            yield projection


class CommunityItem(RecordItem):
    """Single request result."""

    @property
    def links(self):
        """Get links for this result item."""
        return self._links_tpl.expand(self._identity, self._record)

    def to_dict(self):
        """Get a dictionary for the request."""
        res = self.data
        if self._errors:
            res["errors"] = self._errors
        return res


class FeaturedCommunityItem(CommunityItem):
    """Single request result."""
