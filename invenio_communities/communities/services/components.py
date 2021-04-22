# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from invenio_access.permissions import system_process
from invenio_rdm_records.services.components import AccessComponent
from invenio_records_resources.services.records.components import \
    ServiceComponent
from marshmallow.exceptions import ValidationError


class PIDComponent(ServiceComponent):
    """Service component for Community PIDs."""

    def create(self, identity, record=None, data=None, **kwargs):
        """Create a Community PID from its metadata."""
        record['id'] = data['id']
        provider = record.__class__.pid.field._provider.create(record=record)
        setattr(record, 'pid', provider.pid)

    def update(self, identity, record=None, data=None, **kwargs):
        """Rename the Community PIDs value."""
        if 'id' in data and record.pid.pid_value != data['id']:
            raise ValidationError(
                'The ID should be modified through the renaming URL instead',
                'id')

    def rename(self, identity, record=None, data=None, **kwargs):
        """Rename the Community PIDs value."""
        if record.pid.pid_value == data['id']:
            raise ValidationError(
                'A new ID value is required for the renaming', 'id')

        record.__class__.pid.field._provider.update(
            record.pid, data['id'])


class CommunityAccessComponent(AccessComponent):
    """Service component for access integration."""

    def _populate_access_and_validate(self, identity, data, record, **kwargs):
        """Populate and validate the community's access field."""
        if record is not None and "access" in data:
            # populate the record's access field with the data already
            # validated by marshmallow
            record.setdefault('access', {})
            record['access'].update(data.get("access", {}))
            record.access.refresh_from_dict(record.get("access"))

    def _init_owners(self, identity, record, **kwargs):
        """If the record has no owners yet, add the current user."""
        # if the given identity is that of a user, we add the
        # corresponding user to the owners (record.access.owned_by)
        is_sys_id = system_process in identity.provides
        if not record.access.owned_by and not is_sys_id:
            record.access.owned_by.add({"user": identity.id})

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the record."""
        self._populate_access_and_validate(identity, data, record, **kwargs)
        self._init_owners(identity, record, **kwargs)

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        self._populate_access_and_validate(identity, data, record, **kwargs)
