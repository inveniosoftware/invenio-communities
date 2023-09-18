# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the tombstone field and community deletion field."""

import datetime

import pytest
from invenio_requests.resolvers.registry import ResolverRegistry

from invenio_communities.communities.records.api import Community
from invenio_communities.communities.records.systemfields.deletion_status import (
    CommunityDeletionStatus,
    CommunityDeletionStatusEnum,
)
from invenio_communities.communities.records.systemfields.tombstone import Tombstone

#
# Tombstone
#


def test_tombstone_creation(app):
    """Test the normal creation of a tombstone."""
    t = Tombstone({})
    assert t.removed_by is None
    assert t.removal_reason is None
    assert t.note == ""
    assert t.removal_date
    assert isinstance(t.removal_date, str)
    assert t.citation_text == ""
    assert t.is_visible

    data = {
        "removed_by": {"user": "1"},
        "removal_reason": {"id": "spam"},
        "note": "nothing in particular",
        "removal_date": datetime.datetime.utcnow(),
        "citation_text": "No citation available, sorry",
        "is_visible": False,
    }

    t = Tombstone(data)
    assert t.removed_by == data["removed_by"]
    assert t.removal_reason == data["removal_reason"]
    assert t.note == data["note"]
    assert t.removal_date == data["removal_date"].isoformat()
    assert t.citation_text == data["citation_text"]
    assert not t.is_visible


def test_tombstone_invalid_removed_by(app):
    """Test the failure of tombstone creation if the `removed_by` entry is invalid."""
    for invalid_value in [[], datetime.datetime.utcnow()]:
        with pytest.raises(ValueError):
            Tombstone({"removed_by": invalid_value})


def test_tombstone_valid_removed_by(app, users):
    """Test various ways to set the `removed_by` value for a tombstone."""
    user = users["owner"].user

    # if the assigned value is an int or string, we assume it's a user ID
    t = Tombstone({})
    t.removed_by = user.id
    assert t.removed_by == {"user": str(user.id)}
    assert t.removed_by_proxy.resolve() == user

    # this comes in handy for setting the system to be the one who deleted the community
    t.removed_by = "system"
    assert t.removed_by == {"user": "system"}
    assert t.removed_by_proxy.resolve() == {
        "id": "system",
        "is_ghost": True,
        "profile": {"full_name": "System"},
        "username": "System",
    }

    # None should work as expected
    t.removed_by = None
    assert t.removed_by is None
    assert t.removed_by_proxy is None

    # setting a referenceable entity should use the `ResolverRegistry`
    t.removed_by = user
    assert ResolverRegistry.reference_entity(user) is not None
    assert t.removed_by == {"user": str(user.id)}
    assert t.removed_by_proxy.resolve() == user


#
# Community deletion status
#


def test_community_deletion_status_default(app):
    """Test the default value of the deletion status."""
    deletion_status = CommunityDeletionStatus(None)
    assert deletion_status.status == CommunityDeletionStatusEnum.PUBLISHED.value
    assert not deletion_status.is_deleted


def test_community_deletion_status_valid_values(app):
    """Test setting the deletion status to valid values."""
    deletion_status = CommunityDeletionStatus(CommunityDeletionStatusEnum.PUBLISHED)
    assert deletion_status.status == CommunityDeletionStatusEnum.PUBLISHED.value
    assert not deletion_status.is_deleted

    deletion_status.status = CommunityDeletionStatusEnum.DELETED
    assert deletion_status.status == CommunityDeletionStatusEnum.DELETED.value
    assert deletion_status.is_deleted

    deletion_status.status = CommunityDeletionStatusEnum.MARKED
    assert deletion_status.status == CommunityDeletionStatusEnum.MARKED.value
    assert deletion_status.is_deleted


def test_community_deletion_status_invalid_values(app):
    """Test setting the community deletion status to invalid values."""
    for invalid_value in ["s", 1, []]:
        with pytest.raises(ValueError):
            CommunityDeletionStatus(invalid_value)


def test_community_deletion_status(app, location, minimal_community):
    """Test if changing the community deletion status impacts the DB model."""
    minimal_community = minimal_community.copy()
    slug = minimal_community.pop("slug")

    comm = Community.create(minimal_community, slug=slug)
    assert comm.deletion_status.status == CommunityDeletionStatusEnum.PUBLISHED.value
    assert comm.deletion_status._status == CommunityDeletionStatusEnum.PUBLISHED
    assert (
        CommunityDeletionStatus(comm.model.deletion_status)
        == CommunityDeletionStatusEnum.PUBLISHED
    )
    assert not comm.deletion_status.is_deleted
    assert not comm.is_deleted

    # NOTE that the `community.deletion_status.is_deleted` relates to the
    #      community deletion workflow, while `community.is_deleted` is defined
    #      in `invenio_records.api.RecordBase` and marks the absolute deletion
    #      of the community
    comm.deletion_status = CommunityDeletionStatusEnum.DELETED
    assert comm.deletion_status.status == CommunityDeletionStatusEnum.DELETED.value
    assert comm.deletion_status._status == CommunityDeletionStatusEnum.DELETED
    assert (
        CommunityDeletionStatusEnum(comm.model.deletion_status)
        == CommunityDeletionStatusEnum.DELETED
    )
    assert comm.deletion_status.is_deleted
    assert not comm.is_deleted
