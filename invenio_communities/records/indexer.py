
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community records indexing receivers."""

from invenio_communities.records.api import Record, RecordCommunitiesCollection


def record_indexer_receiver(sender, json=None, record=None, **kwargs):
    """Add communities information to record.

    To integrate this indexer you need to add to your record's ES mapping the
    following ``_communities`` property:

    ..code-block:: json

    {
        "_communities": {
            "type": "object",
            "properties": {
                "accepted": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "keyword",
                        },
                        "comid": {
                            "type": "keyword",
                        }
                        "title": {
                            "type": "text",
                        },
                        "request_id": {
                            "type": "keyword",
                        }
                        "created_by": {
                            "type": "integer",
                        }
                    }
                },
                "pending": {
                    <same structure as accepted>
                },
                "rejected": {
                    <same structure as accepted>
                }
            }
        }
    }
    """
    # TODO: Remove when the PID mixin is in the base record class
    _record = Record(record, model=record.model)
    json['_communities'] = RecordCommunitiesCollection(_record).as_dict()
