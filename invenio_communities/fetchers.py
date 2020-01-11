# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
from __future__ import absolute_import, print_function

from invenio_pidstore.fetchers import FetchedPID


def comid_fetcher(record_uuid, data):
    """Fetch a community's identifier."""
    return FetchedPID(provider=None, pid_type='comid', pid_value=data['id'])
