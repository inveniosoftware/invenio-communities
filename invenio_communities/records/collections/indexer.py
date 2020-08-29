
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community collections record indexing receivers."""

from invenio_communities.records.api import Record, RecordCommunitiesCollection


def record_collections_indexer_receiver(sender, json=None, record=None,
        **kwargs):
    """Add community collections information to record.

    To integrate this indexer you need to add to your record's ES mapping the
    following ``_communities_collections`` property:

    ..code-block:: json

    {
        "_communities_collections": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "order": {
                    "type": "integer"
                }
            }
        }
    }
    """
    # TODO: Remove when the PID mixin is in the base record class
    _record = Record(record, model=record.model)
    communities_collections = []
    for community_record in RecordCommunitiesCollection(_record):
        comid = community_record.model.community_pid.pid_value
        for col in community_record.get('_collections', []):
            communities_collections.append({
                'id': '{}:{}'.format(comid, col['id'])
            })

    json['_communities_collections'] = communities_collections
