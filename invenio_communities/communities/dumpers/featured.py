# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022-2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Featured timestamp dumper.

Dumper used to dump/load the featured times of a record to/from an
search body.
"""

from datetime import datetime

from invenio_db import db
from invenio_records.dumpers import SearchDumperExt

from invenio_communities.communities.records.models import CommunityFeatured


class FeaturedDumperExt(SearchDumperExt):
    """Dumper for the featured field."""

    def __init__(self, key="featured"):
        """Initialize the dumper."""
        self.key = key

    def dump(self, record, data):
        """Dump featured entries."""
        now_ = datetime.utcnow()
        future_entries = (
            db.session.query(CommunityFeatured)
            .filter(
                CommunityFeatured.community_id == record.id,
                CommunityFeatured.start_date > now_,
            )
            .order_by(CommunityFeatured.start_date.desc())
            .all()
        )

        past_entries = (
            db.session.query(CommunityFeatured)
            .filter(
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
