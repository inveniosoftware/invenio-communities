# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Community status system field."""

import enum

from invenio_records.systemfields import SystemField


class CommunityStatusEnum(enum.Enum):
    """Community status enum."""

    NEW = "new"
    VERIFIED = "verified"
    MODERATED = "moderated"


class CommunityStatus:
    """The community status of the community."""

    def __init__(self, status):
        """Initialize the community status."""
        self.status = status

    @property
    def status(self):
        """Get the community status."""
        return self._status.value

    @status.setter
    def status(self, value):
        """Set the community status."""
        if value is None:
            self._status = CommunityStatusEnum.NEW

        elif isinstance(value, str):
            self._status = CommunityStatusEnum(value)

        elif isinstance(value, CommunityStatusEnum):
            self._status = value

        else:
            raise ValueError(f"Invalid value for community community status: {value}")

    def __repr__(self):
        """Return repr(self)."""
        return f"<CommunityStatus {self._status.name}: '{self._status.value}'>"

    def __str__(self):
        """Return str(self)."""
        return self.status

    def __eq__(self, other):
        """Check if self and other are equal.

        This allows checking against other instances of the same type, strings,
        and ``CommunityStatusEnum`` values.
        """
        if isinstance(other, type(self)):
            return self.status == other.status

        elif isinstance(other, CommunityStatusEnum):
            return self.status == other.value

        elif isinstance(other, str):
            return self.status == other

        return False


class CommunityStatusField(SystemField):
    """System field for the community status."""

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the status of the community."""
        if record is None:
            return self  # returns the field itself.

        status = self._get_cache(record) or CommunityStatus(record.get("status"))

        self._set_cache(record, status)
        return status

    def __set__(self, record, value):
        """Set the status of the community."""
        status = CommunityStatus(value)
        self._set_cache(record, status)

    def pre_commit(self, record):
        """Dump the deletion status to the community before committing."""
        status = self._get_cache(record) or CommunityStatus(None)
        record[self.key] = status.status
