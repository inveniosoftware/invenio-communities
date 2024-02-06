# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community PID slug field."""
from uuid import UUID

from invenio_records.systemfields import SystemField
from sqlalchemy.orm.exc import NoResultFound


def is_valid_uuid(value):
    """Check if the provided value is a valid UUID."""
    try:
        UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


class ParentCommunityField(SystemField):
    """System field for parent community."""

    def __init__(self, key="parent"):
        """Create a new ParentCommunityField instance."""
        super().__init__(key=key)

    def obj(self, instance):
        """Get the access object."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        value = self.get_dictkey(instance)
        if value:
            obj = instance.get_record(value["id"])
        else:
            obj = None

        self._set_cache(instance, obj)
        return obj

    def set_obj(self, record, obj):
        """Set the access object."""
        # Check if obj is None and remove 'parent' key from record
        if obj is None:
            record.pop("parent", None)
            return
        if is_valid_uuid(obj):
            try:
                # Attempt to retrieve the community to confirm its existence
                parent_community = record.get_record(obj)
                record["parent"] = {"id": str(parent_community.id)}
                self._set_cache(record, parent_community)
            except NoResultFound as e:
                raise ValueError("Community does not exist.") from e
        elif isinstance(obj, type(record)):
            record["parent"] = {"id": str(obj.id)}
        else:
            raise ValueError("Invalid parent community.")

    def __get__(self, record, owner=None):
        """Get the record's access object."""
        if record is None:
            # access by class
            return self

        # access by object
        return self.obj(record)

    def __set__(self, record, obj):
        """Set the records access object."""
        self.set_obj(record, obj)
