# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from invenio_records_resources.services.records.components import \
    ServiceComponent


class PIDComponent(ServiceComponent):
    """Service component for Community PIDs."""

    def create(self, identity, record=None, **kwargs):
        """Create a Community PID from its metadata."""
        provider = record.__class__.pid.field._provider.create(record=record)
        setattr(record, 'pid', provider.pid)

    def update(self, identity, record=None, **kwargs):
        """Update the Community PIDs value."""
        if record.pid.pid_value != record['id']:
            record.__class__.pid.field._provider.update(
                record.pid, record['id'])
