# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community PID slug field."""

from uuid import UUID

from invenio_records.dictutils import filter_dict_keys
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
            self._set_cache(record, None)
            return

        if isinstance(obj, type(record)):
            parent_community = obj
        elif is_valid_uuid(obj):
            try:
                # Attempt to retrieve the community to confirm its existence
                parent_community = record.get_record(obj)
            except NoResultFound as e:
                raise ValueError("Community does not exist.") from e
        else:
            raise ValueError("Invalid parent community.")

        # Store the community ID in the record JSON
        record["parent"] = {"id": str(parent_community.id)}
        # Cache the community object
        self._set_cache(record, parent_community)

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

    def post_dump(self, record, data, dumper=None):
        """After dumping, dereference the parent community."""
        parent_community = getattr(record, self.attr_name)
        if parent_community:
            dump = parent_community.dumps()

            # Add a version counter "@v" used for optimistic concurrency control. It
            # allows to search for all outdated community references and reindex them
            dump["@v"] = f"{parent_community.id}::{parent_community.revision_id}"

            data[self.key] = filter_dict_keys(
                dump,
                keys=[
                    "@v",
                    "uuid",
                    "created",
                    "updated",
                    "id",
                    "slug",
                    "theme",
                    "version_id",
                    "children.allow",
                    "metadata.title",
                    "metadata.type",
                    "metadata.website",
                    "metadata.organizations",
                    "metadata.funding",
                ],
            )

    def post_load(self, record, data, loader=None):
        """Laod the parent community using the OS data (preventing a DB query)."""
        if data.get("parent"):
            record.parent = record.loads(data["parent"])
