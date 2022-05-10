# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members service."""

from invenio_records_resources.services.uow import Operation
from invenio_records_resources.tasks import send_change_notifications


class ChangeNotificationOp(Operation):
    """A change notification operation.

    Need to overwrite the records-resources operation
    since members have no pid and so the first param ought
    to be the uuid.
    """

    def __init__(self, record_type, records):
        """Constructor."""
        self._record_type = record_type
        self._records = records

    def on_post_commit(self, uow):
        """Send the notification (run celery task).

        Other record types (e.g. requests) do not link by member
        but by the user that's a member and that's why we propagate
        the user id/version.
        """
        send_change_notifications.delay(
            self._record_type,
            [
                (str(r["user"]["id"]), str(r.id), r["user"]["@v"])
                for r in self._records
            ]
        )
