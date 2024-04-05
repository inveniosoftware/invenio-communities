# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Communities system field."""

from invenio_records.dictutils import filter_dict_keys
from invenio_records.systemfields import SystemField

from .context import CommunitiesFieldContext
from .manager import CommunitiesRelationManager


class CommunitiesField(SystemField):
    """Communities system field for managing relations to communities."""

    def __init__(
        self, m2m_model_cls, key="communities", context_cls=None, manager_cls=None
    ):
        """Constructor."""
        self._m2m_model_cls = m2m_model_cls
        self._context_cls = context_cls or CommunitiesFieldContext
        self._manager_cls = manager_cls or CommunitiesRelationManager
        super().__init__(key=key)

    #
    # Life-cycle hooks
    #
    def pre_commit(self, record):
        """Commit the communities field."""
        manager = self.obj(record)
        self.set_dictkey(record, manager.to_dict())

    #
    # Helpers
    #
    def obj(self, record):
        """Get or create the communities manager."""
        # Check cache
        obj = self._get_cache(record)
        if obj is not None:
            return obj

        data = self.get_dictkey(record)
        # Create manager
        obj = self._manager_cls(self._m2m_model_cls, record.id, data)
        self._set_cache(record, obj)
        return obj

    # Data descriptor methods (i.e. attribute access)
    # __set__() not defined on purpose
    def __get__(self, record, owner=None):
        """Get the persistent identifier."""
        if record is None:
            return self._context_cls(self, owner)
        return self.obj(record)

    def post_dump(self, record, data, dumper=None):
        """Dump the communities field."""
        comms = getattr(record, self.attr_name)
        res = comms.to_dict()

        def _dump_community(comm):
            dump = comm.dumps()

            # Add a version counter "@v" used for optimistic concurrency control. It
            # allows to search for all outdated community references and reindex them
            dump["@v"] = f"{comm.id}::{comm.revision_id}"

            return filter_dict_keys(
                dump,
                keys=[
                    "@v",
                    "uuid",
                    "created",
                    "updated",
                    "id",
                    "slug",
                    "theme",
                    "is_verified",
                    "version_id",
                    "metadata.title",
                    "metadata.type",
                    "metadata.website",
                    "metadata.organizations",
                    "metadata.funding",
                    "children.allow",
                    "parent.id",
                    "parent.slug",
                    "parent.uuid",
                    "parent.created",
                    "parent.updated",
                    "parent.version_id",
                    "parent.theme",
                    "parent.is_verified",
                    "parent.children.allow",
                    "parent.metadata.title",
                    "parent.metadata.type",
                    "parent.metadata.website",
                    "parent.metadata.organizations",
                    "parent.metadata.funding",
                ],
            )

        if res:
            res["entries"] = [_dump_community(comm) for comm in comms]
            data[self.key] = res

    def post_load(self, record, data, loader=None):
        """Load the parent community using the OS data (preventing a DB query)."""
        comms = data.get("communities")
        if comms:
            obj = self._manager_cls(self._m2m_model_cls, record.id, comms)
            self._set_cache(record, obj)
