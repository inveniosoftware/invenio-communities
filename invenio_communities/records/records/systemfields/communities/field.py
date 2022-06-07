# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Communities system field."""

from invenio_records.systemfields import SystemField

from .context import CommunitiesFieldContext
from .manager import CommunitiesRelationManager


class CommunitiesField(SystemField):
    """Communites system field for managing relations to communities."""

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
        """Get or crate the communities manager."""
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
