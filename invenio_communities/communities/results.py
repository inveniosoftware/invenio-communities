# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# In is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service results."""


from invenio_records_resources.config import lt_es7
from invenio_records_resources.pagination import Pagination
from invenio_records_resources.services.base import ServiceItemResult, \
    ServiceListResult


class CommunityItem(ServiceItemResult):

    def __init__(self, service, identity, record, errors=None,
                 links_tpl=None, schema=None):
        """Constructor."""
        self._errors = errors
        self._identity = identity
        self._links_tpl = links_tpl
        self._record = record
        self._service = service
        self._schema = schema or service.schema
        self._data = None

    @property
    def id(self):
        """Get the community id."""
        return self._record.pid.pid_value

    def __getitem__(self, key):
        """Key a key from the data."""
        return self.data[key]

    @property
    def links(self):
        """Get links for this result item."""
        return self._links_tpl.expand(self._record)

    @property
    def _obj(self):
        """Return the object to dump."""
        return self._record

    @property
    def data(self):
        """Property to get the community."""
        if self._data:
            return self._data

        self._data = self._schema.dump(
            self._obj,
            context=dict(
                identity=self._identity,
                record=self._record,
            )
        )
        if self._links_tpl:
            self._data["links"] = self.links

        return self._data

    def to_dict(self):
        """Get a dictionary for the community."""
        res = self.data
        if self._errors:
            res['errors'] = self._errors
        return res

    def has_permissions_to(self, actions):
        """Returns dict of "can_<action>": bool.

        Placing this functionality here because it is a projection of the
        community item's characteristics and allows us to re-use the
        underlying data layer community. Because it is selective about the actions
        it checks for performance reasons, it is not embedded in the `to_dict`
        method.

        :params actions: list of action strings
        :returns dict:

        Example:
        community_item.permissions_to(["update_draft", "read_files"])
        {
            "can_update_draft": False,
            "can_read_files": True
        }
        """
        return {
            f"can_{action}": self._service.check_permission(
                self._identity, action, record=self._record
            )
            for action in actions
        }


class CommunityList(ServiceListResult):
    """List of communitys result."""

    def __init__(self, service, identity, results, params, links_tpl=None,
                 links_item_tpl=None, schema=None):
        """Constructor.

        :params service: a service instance
        :params identity: an identity that performed the service request
        :params results: the search results
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
        if hasattr(self._results, 'hits'):
            if lt_es7:
                return self._results.hits.total
            else:
                return self._results.hits.total["value"]
        else:
            # handle scan(): returns a generator
            return None

    @property
    def aggregations(self):
        """Get the search result aggregations."""
        return self._results.aggregations.to_dict()

    @property
    def hits(self):
        """Iterator over the hits."""
        for hit in self._results:
            # Load dump
            record = self._service.record_cls.loads(hit.to_dict())

            # Project the rec
            projection = self._schema.dump(
                record,
                context=dict(
                    identity=self._identity,
                    record=record,
                )
            )
            # TODO: Communities-issue
            # if self._links_item_tpl:
            #     projection['links'] = self._links_item_tpl.expand(record)

            yield projection

    @property
    def pagination(self):
        """Create a pagination object."""
        return Pagination(
            self._params['size'],
            self._params['page'],
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
            },
            "sortBy": self._params["sort"],
            "aggregations": self.aggregations,
        }
        if self._links_tpl:
            res['links'] = self._links_tpl.expand(self.pagination)
        return res
