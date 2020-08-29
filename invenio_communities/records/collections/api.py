# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record collections API."""

from __future__ import absolute_import, print_function

from invenio_communities.api import Community


class CommunityCollection(dict):

    def __init__(self, data, id_=None, community=None):
        self.id = id_
        self.community = community
        super(CommunityCollection, self).__init__(data)

    def commit(self):
        self.community.commit()
        return self


class CommunityCollectionsMap(object):

    community_cls = Community

    def __init__(self, community):
        self.community = community

    @property
    def _collections(self):
        return self.community.get('_collections', {})

    def __len__(self):
        """Get number of community collections."""
        return len(self._collections)

    def __iter__(self):
        self._it = iter(self._collections.items())
        return self

    def __next__(self):
        """Get next community collection."""
        id_, data = next(self._it)
        return CommunityCollection(
            data, id_=id_, community=self.community)

    def __getitem__(self, collection_id):
        """Get a specific collection by ID."""
        return CommunityCollection(
            self._collections[collection_id], id_=collection_id,
            community=self.community)

    def __delitem__(self, collection_id):
        """Delete a collection by its ID."""
        return self.remove(collection_id)

    def __contains__(self, collection_id):
        return collection_id in self._collections

    def add(self, collection_id, **data):
        self.community.setdefault('_collections', {})
        self.community['_collections'][collection_id] = data
        # TODO: Do this here, or should the caller know and commit?
        self.community.commit()
        return self[collection_id]

    def remove(self, collection_id):
        if collection_id in self._collections:
            del self.community['_collections'][collection_id]
        # TODO: Do this here, or should the caller know and commit?
        self.community.commit()

    def as_dict(self):
        return self._collections


class CommunityCollectionsMixin(object):

    @property
    def collections(self):
        return CommunityCollectionsMap(self)


class CommunityRecordCollectionsMap(object):

    community_cls = Community

    def __init__(self, community_record):
        self.community_record = community_record

    @property
    def _collections(self):
        return self.community_record.get('_collections')

    def __len__(self):
        """Get number of community collections."""
        return len(self._collections)

    def __iter__(self):
        self._it = iter(self._collections)
        return self

    def __next__(self):
        """Get next community collection."""
        collection_id, collection_data = next(self._it)
        return {'id': collection_id, **collection_data}

    def __getitem__(self, collection_id):
        """Get a specific collection by its ID."""
        return self._collections[collection_id]

    def __delitem__(self, collection_id):
        """Delete a collection by its ID."""
        return self.remove(collection_id)

    def __contains__(self, collection_id):
        return collection_id in self._collections

    def add(self, collection_id, **data):
        self.community.setdefault('_collections', {})
        self.community['_collections'][collection_id] = data
        self.community.commit()
        return self[collection_id]

    def remove(self, collection_id):
        if collection_id in self._collections:
            del self.community['_collections'][collection_id]
        self.community.commit()


class CommunityRecordCollectionsMixin(object):

    @property
    def collections(self):
        return CommunityRecordCollectionsMap(self)
