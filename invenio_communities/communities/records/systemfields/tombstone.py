# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Systemfield for managing tombstone information of a community."""

from datetime import datetime

from invenio_records.systemfields import SystemField
from invenio_requests.resolvers.registry import ResolverRegistry


class Tombstone:
    """A data class for managing tombstone information."""

    def __init__(self, data):
        """Constructor."""
        self.removal_reason = data.get("removal_reason")
        self.note = data.get("note")
        self.removed_by = data.get("removed_by")
        self.removal_date = data.get("removal_date")
        self.citation_text = data.get("citation_text")
        self.is_visible = data.get("is_visible", True)

    @property
    def removal_reason(self):
        """Get the removal reason."""
        return self._removal_reason

    @removal_reason.setter
    def removal_reason(self, value):
        """Set the removal reason, referencing the corresponding vocabulary.

        If the value is a string, it will be turned into a dictionary of the
        shape ``{"id": value}``.
        """
        # NOTE: the validity of the reference is checked
        #       in the record's relations systemfield
        if isinstance(value, str):
            value = {"id": value}

        self._removal_reason = value

    @property
    def note(self):
        """Get the public note attached to the tombstone."""
        return self._note

    @note.setter
    def note(self, value):
        """Set the public note attached to the tombstone."""
        self._note = value or ""

    @property
    def removed_by(self):
        """Get a reference to the entity who removed the record."""
        return self._removed_by

    @removed_by.setter
    def removed_by(self, value):
        """Set a reference to the entity who removed the record.

        If the value is a string or integer, it is assumed that the
        reference is a user and the value will be turned into a dictionary
        of the shape ``{"user": value}``.
        If the value is a referenceable entity (such as a ``User`` object),
        the ``ResolverRegistry`` will be used to create a reference dict.
        """
        if value is None:
            self._removed_by = None

        elif (ref := ResolverRegistry.reference_entity(value)) is not None:
            self._removed_by = ref

        elif isinstance(value, (int, str)):
            self._removed_by = {"user": str(value)}

        else:
            raise ValueError(f"Invalid value for 'tombstone.removed_by': {value}")

    @property
    def removal_date(self):
        """Get the removal date."""
        return self._removal_date

    @removal_date.setter
    def removal_date(self, value):
        """Set the removal date."""
        if value is None:
            value = datetime.utcnow()

        if isinstance(value, datetime):
            value = value.isoformat()

        self._removal_date = value

    @property
    def citation_text(self):
        """Get the citation text of the tombstoned community."""
        return self._citation_text

    @citation_text.setter
    def citation_text(self, value):
        """Set the citation text of the tombstoned community."""
        self._citation_text = value or ""

    @property
    def is_visible(self):
        """Check if the tombstone is publicly visible."""
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        """Set the public visibility of the tombstone."""
        self._is_visible = bool(value)

    @property
    def removed_by_proxy(self):
        """Resolve the entity proxy for ``self.removed_by``."""
        if self.removed_by is None:
            return None
        else:
            return ResolverRegistry.resolve_entity_proxy(self.removed_by)

    def dump(self):
        """Dump the tombstone into a dictionary."""
        data = {
            "note": self.note,
            "removed_by": self.removed_by,
            "removal_date": self.removal_date,
            "citation_text": self.citation_text,
            "is_visible": self.is_visible,
        }

        if self.removal_reason:
            data["removal_reason"] = self.removal_reason

        return data

    def __repr__(self):
        """Return repr(self)."""
        return repr(self.dump())


class TombstoneField(SystemField):
    """System field for accessing a community's deletion status."""

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the persistent identifier."""
        if record is None:
            return self  # returns the field itself.

        tombstone = self._get_cache(record)
        if tombstone is not None:
            return tombstone

        ts_dict = record.get("tombstone", None)
        tombstone = Tombstone(ts_dict) if ts_dict else None
        self._set_cache(record, tombstone)
        return tombstone

    def __set__(self, record, value):
        """Set a community's tombstone entry."""
        if value is None:
            tombstone = None
        elif isinstance(value, dict):
            tombstone = Tombstone(value)
        elif isinstance(value, Tombstone):
            tombstone = value
        else:
            raise ValueError(f"Invalid type for tombstone: {value}")

        self._set_cache(record, tombstone)

    def pre_commit(self, record):
        """Dump the configured tombstone before committing the community record."""
        tombstone = self._get_cache(record)
        if tombstone:
            record["tombstone"] = tombstone.dump()
        else:
            record.pop("tombstone", None)
