# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test communities types relationships."""


#
# Tests
#

from copy import deepcopy

import pytest
from invenio_records.systemfields.relations.errors import InvalidRelationValue

from invenio_communities.communities.records.api import Community


@pytest.fixture(scope="module")
def minimal_community(minimal_community):
    minimal_community.pop("slug")
    return minimal_community


@pytest.mark.parametrize(
    "community_type, expected",
    [
        ("organization", "organization"),
        ("event", "event"),
        ("topic", "topic"),
        ("project", "project"),
    ],
)
def test_valid_community_types(
    db, location, minimal_community, community_type, expected, community_type_record
):
    community_copy = deepcopy(minimal_community)
    community_copy["metadata"].update({"type": {"id": community_type}})

    comm = Community.create(community_copy, slug="test")
    comm.commit()
    db.session.commit()

    assert comm.metadata["type"]["id"] == expected


def test_invalid_community_type(db, minimal_community, community_type_record):
    community_copy = deepcopy(minimal_community)
    community_copy["metadata"].update({"type": {"id": "invalid_type"}})
    with pytest.raises(InvalidRelationValue):
        comm = Community.create(community_copy, slug="test")
        comm.commit()
        db.session.commit()


def test_organizations_field():
    """organizations should be defined as a relation."""
    assert "type" in Community.relations
    assert Community.relations.organizations
