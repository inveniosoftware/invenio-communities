# SPDX-FileCopyrightText: 2026 divyanshu-iitian.
# SPDX-License-Identifier: MIT

"""Tests for community administration views."""

from datetime import datetime, timedelta, timezone

from invenio_communities.administration.communities import (
    CommunityDetailView,
    CommunityListView,
    _featured_community_initial_values,
)


def test_featured_community_start_date_initial_value():
    """Start feature-community actions at the current UTC minute."""
    before = datetime.now(timezone.utc)
    values = _featured_community_initial_values()
    after = datetime.now(timezone.utc)
    start_date = datetime.fromisoformat(values["start_date"])

    assert before - timedelta(minutes=1) < start_date <= after
    assert start_date.second == 0
    assert start_date.microsecond == 0
    assert (
        CommunityListView.actions["featured"]["initial_values"]
        is _featured_community_initial_values
    )
    assert (
        CommunityDetailView.actions["featured"]["initial_values"]
        is _featured_community_initial_values
    )
