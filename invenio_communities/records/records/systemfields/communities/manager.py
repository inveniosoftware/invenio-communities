# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Community relations manager.

The manager provides the API to add, remove and iterate over communities
associated with a record.
"""

from invenio_db import db
from invenio_records.api import Record

from invenio_communities.communities.records.api import Community


class CommunitiesRelationManager:
    """Manager for a record's community relations."""

    def __init__(self, m2m_model_cls, record_id, data):
        """Constructor."""
        self._m2m_model_cls = m2m_model_cls
        self._record_id = record_id
        self._default_id = None
        self._communities_ids = set()
        self._communities_cache = {}
        self.from_dict(data)

    #
    # Helpers
    #
    def _to_id(self, val):
        """Get the community id."""
        if isinstance(val, str):
            return val
        elif isinstance(val, Record):
            return str(val.id)
        return None

    def _lookup_community(self, community_id):
        """Retrieve a community by id.

        Caches the community.
        """
        if community_id not in self._communities_cache:
            c = Community.get_record(community_id)
            self._communities_cache[str(c.id)] = c
        return self._communities_cache[community_id]

    #
    # API
    #
    def add(self, community_or_id, request=None, default=False):
        """Add a record to a community.

        If a record was already added to a community an IntegrityError will
        be raised.
        """
        community_id = self._to_id(community_or_id)

        # Create M2M object
        obj = self._m2m_model_cls(
            record_id=self._record_id,
            community_id=community_id,
            request_id=self._to_id(request),
        )
        db.session.add(obj)

        # Add to internal set
        self._communities_ids.add(community_id)

        # Set default
        if default:
            self._default_id = community_id

        # Cache community only if provided
        if isinstance(community_or_id, Community):
            self._communities_cache[community_id] = community_or_id

    def remove(self, community_or_id):
        """Remove a record from a community."""
        community_id = self._to_id(community_or_id)

        # Delete M2M row.
        res = self._m2m_model_cls.query.filter_by(
            community_id=community_id, record_id=self._record_id
        ).delete()
        if res != 1:
            raise ValueError("The record has not been added to the community.")

        # Remove from internal set
        self._communities_ids.remove(community_id)

        # Unset default if needed
        if self._default_id == community_id:
            self._default_id = None

    def clear(self):
        """Clear all communities from the record."""
        # Remove all associations
        res = self._m2m_model_cls.query.filter_by(record_id=self._record_id).delete()
        self._communities_ids = set()
        self._default_id = None
        self._communities_cache = {}

    def refresh(self):
        """Refresh from the database M2M table."""
        # Retrieve from M2M table
        ids = (
            db.session.query(self._m2m_model_cls.community_id)
            .filter(self._m2m_model_cls.record_id == self._record_id)
            .all()
        )

        # Set internal list
        self._communities_ids = set([str(x[0]) for x in ids])

        # Unset default if no longer available
        if self._default_id and self._default_id not in self._communities_ids:
            self._default_id = None

    def __len__(self):
        """Get number of communities."""
        return len(self._communities_ids)

    def __contains__(self, community_or_id):
        """Check record is in community."""
        id_ = self._to_id(community_or_id)
        return id_ in self._communities_ids

    def __iter__(self):
        """Iterate over a communities."""
        # Determine community ids not already cached.
        nocache_ids = self._communities_ids - set(self._communities_cache.keys())

        # Fetch and cache missing community records
        if nocache_ids:
            communities = Community.get_records(nocache_ids)
            for c in communities:
                self._communities_cache[str(c.id)] = c

        # Iterate (sort by identifier to ensure consistent results)
        return (self._communities_cache[c] for c in sorted(self._communities_ids))

    @property
    def ids(self):
        """Get communities ids."""
        return sorted(self._communities_ids)

    @property
    def default(self):
        """Get the default community."""
        if self._default_id is not None:
            return self._lookup_community(self._default_id)
        return None

    @default.setter
    def default(self, community_or_id):
        """Set the default community.

        Note, the community must already have been added to the community. If
        not, then use ``.add(community, default=True)`` instead.
        """
        id_ = self._to_id(community_or_id)
        if id_ not in self._communities_ids:
            raise AttributeError(
                "Cannot set community as the default. "
                "The record has not been added to the community."
            )
        self._default_id = id_

    @default.deleter
    def default(self):
        self._default_id = None

    # Persist relationships in record (denormalize the M2M table).
    # This enables 1) tracking community membership via the record versioning
    # and 2) faster indexing by not having to query the database for
    # relationships.
    def to_dict(self):
        """Get the dictionary which will be stored in the record."""
        data = {}
        if self._default_id is not None:
            data["default"] = self._default_id
        ids = list(self.ids)
        if ids:
            data["ids"] = ids
        return data

    def from_dict(self, data):
        """Build manager from the record dict."""
        data = data or {}
        self._default_id = data.get("default", None)
        self._communities_ids = set(data.get("ids", []))
        return self
