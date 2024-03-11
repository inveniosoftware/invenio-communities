# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2023-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Children system field."""

from invenio_records.systemfields import SystemField


class Children:
    """Children object."""

    def __init__(self, allow=None):
        """Create a Children object."""
        self.dirty = allow is not None
        self._allow = allow or False

    @property
    def allow(self):
        """Get the allow."""
        return self._allow

    @allow.setter
    def allow(self, value):
        """Set the allow."""
        if not isinstance(value, bool):
            raise ValueError("Invalid value for allow, it must be a boolean.")
        self._allow = value
        self.dirty = True

    @classmethod
    def from_dict(cls, data):
        """Create a Children object from a dictionary."""
        return cls(allow=data.get("allow"))

    def dump(self):
        """Dump the Children object to a dictionary."""
        return {"allow": self.allow}


class ChildrenField(SystemField):
    """System field for children of a community."""

    children_obj_class = Children

    def __init__(self, key="children", children_obj_class=None):
        """Create a new ChildrenField instance."""
        self._children_obj_class = children_obj_class or self.children_obj_class
        super().__init__(key=key)

    def obj(self, instance):
        """Get the Children object."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        data = self.get_dictkey(instance)
        if data:
            obj = self._children_obj_class.from_dict(data)
        else:
            obj = self._children_obj_class()

        self._set_cache(instance, obj)
        return obj

    def set_obj(self, record, obj):
        """Set the Children object."""
        # We accept both dicts and Children class objects.
        if isinstance(obj, dict):
            obj = self._children_obj_class.from_dict(obj)

        if not isinstance(obj, self._children_obj_class):
            raise ValueError("Invalid children object.")

        # We do not dump the object until the pre_commit hook
        self._set_cache(record, obj)

    def __get__(self, record, owner=None):
        """Get the record's Children object."""
        if record is None:
            # access by class
            return self

        # access by object
        return self.obj(record)

    def __set__(self, record, obj):
        """Set the records Children object."""
        self.set_obj(record, obj)

    def pre_commit(self, record):
        """Dump the configured values before the record is committed."""
        obj = self.obj(record)
        if obj.dirty:
            record[self.key] = obj.dump()
