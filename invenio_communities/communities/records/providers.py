# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""DataCite PID provider."""

from __future__ import absolute_import

import copy

from flask import current_app
from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2


class CommunitiesIdProvider(RecordIdProviderV2):
    """Record identifier provider V2.

    This is the recommended record id provider.

    It generates a random alphanumeric string as opposed to an increasing
    integer (:class:`invenio_pidstore.providers.recordid.RecordIdProvider`).
    """

    pid_type = 'comid'
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name."""
