# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Community PID minters."""

from __future__ import absolute_import, print_function

from invenio_pidstore.models import PersistentIdentifier, PIDStatus


def comid_minter(record_uuid, data):
    """Mint a community PID."""
    assert data.get('id')
    return PersistentIdentifier.create(
        pid_type='comid', pid_value=data['id'],
        object_type='com', object_uuid=record_uuid,
        status=PIDStatus.REGISTERED
    )
