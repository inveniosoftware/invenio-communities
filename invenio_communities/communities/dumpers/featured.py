# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Featured timestamp dumper.

Dumper used to dump/load the featured times of a record to/from an
ElasticSearch body.
"""

from datetime import datetime

from invenio_records.dumpers.elasticsearch import ElasticsearchDumperExt

from invenio_communities.communities.records.models import CommunityFeatured


class FeaturedDumperExt(ElasticsearchDumperExt):
    """Dumper for the featured field."""

    def __init__(self, key="featured"):
        """Initialize the dumper."""
        self.key = key

    def dump(self, record, data):
        """Dump featured entries."""
        now_ = datetime.utcnow()
        future_entries = (
            CommunityFeatured.query.filter(
                CommunityFeatured.community_id == record.id,
                CommunityFeatured.start_date > now_,
            )
            .order_by(CommunityFeatured.start_date.desc())
            .all()
        )

        past_entries = (
            CommunityFeatured.query.filter(
                CommunityFeatured.community_id == record.id,
                CommunityFeatured.start_date <= now_,
            )
            .order_by(CommunityFeatured.start_date.desc())
            .all()
        )

        dumped_field = {}
        dumped_field["future"] = [e.start_date.isoformat() for e in future_entries]
        dumped_field["past"] = [e.start_date.isoformat() for e in past_entries]

        data[self.key] = dumped_field

    def load(self, data, record_cls):
        """Load (remove) indexed data."""
        data.pop(self.key, None)
