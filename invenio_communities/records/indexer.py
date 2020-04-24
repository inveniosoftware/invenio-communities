
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community records indexing receivers."""

from invenio_communities.records.api import RecordCommunitiesCollection


def indexer_receiver(sender, json=None, record=None, index=None, **kwargs):
    """Add community information."""
    if not index.startswith('records-') or record.get('$schema') is None:
        return

    json['communities'] = RecordCommunitiesCollection(record).as_dict()
