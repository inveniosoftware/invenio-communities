# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community PID slug field."""

from uuid import UUID

from invenio_db import db
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records.systemfields import SystemField, SystemFieldContext
from invenio_records_resources.records.api import PersistentIdentifierWrapper


class PIDSlugFieldContext(SystemFieldContext):
    """PID Slug Field Context."""

    def parse_pid(self, value):
        """Parse pid."""
        if isinstance(value, UUID):
            return value
        try:
            return UUID(value)
        except (TypeError, ValueError):
            return value

    def resolve(self, pid_value, registered_only=True):
        """Resolve identifier (either uuid or slug)."""
        pid_value = self.parse_pid(pid_value)

        if isinstance(pid_value, UUID):
            field_name = self.field._id_field
        else:
            field_name = self.field._slug_field
            # Edge case since we allow nullable slug in the database table.
            if not pid_value:
                raise PIDDoesNotExistError("comid", "")

        with db.session.no_autoflush:  # avoid flushing the current session
            model = self.record_cls.model_cls.query.filter_by(
                **{field_name: pid_value}
            ).one_or_none()
            if model is None:
                raise PIDDoesNotExistError("comid", str(pid_value))
            record = self.record_cls(model.data, model=model)
            if record.is_deleted:
                raise PIDDeletedError(PersistentIdentifierWrapper(pid_value), record)
            return record


class PIDSlugField(SystemField):
    """System field for managing record access."""

    def __init__(self, id_field, slug_field):
        """Create a new RecordAccessField instance."""
        self._id_field = id_field
        self._slug_field = slug_field

    def obj(self, record):
        """Get the access object."""
        pid_value = getattr(record, self._id_field)
        if pid_value is None:
            return None
        return PersistentIdentifierWrapper(str(pid_value))

    def __get__(self, record, owner=None):
        """Get the record's access object."""
        if record is None:
            # access by class
            return PIDSlugFieldContext(self, owner)

        # access by object
        return self.obj(record)

    #
    # Life-cycle hooks
    #
    def pre_commit(self, record):
        """Called before a record is committed."""
        # Make sure we don't dump the two model fields into the JSON of the
        # record.
        record.pop(self._id_field, None)
        record.pop(self._slug_field, None)
