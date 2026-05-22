# SPDX-FileCopyrightText: 2022-2024 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Featured timestamp dumper.

Dumper used to dump/load the featured times of a record to/from an
search body.
"""

from datetime import datetime, timezone

from invenio_records.dumpers import SearchDumperExt

from invenio_communities.communities.records.models import CommunityFeatured


class FeaturedDumperExt(SearchDumperExt):
    """Dumper for the featured field."""

    def __init__(self, key="featured"):
        """Initialize the dumper."""
        self.key = key

    def dump(self, record, data):
        """Dump featured entries."""
        now_ = datetime.now(timezone.utc)
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
