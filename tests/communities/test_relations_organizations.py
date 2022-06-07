# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record - organization relationships."""

from copy import deepcopy

import pytest
from invenio_records.systemfields.relations import InvalidRelationValue
from jsonschema.exceptions import ValidationError

from invenio_communities.communities.records.api import Community


@pytest.fixture(scope="module")
def full_community(full_community):
    full_community.pop("slug")
    return full_community


#
# Tests
#
def test_organizations_field(app):
    """organizations should be defined as a relation."""
    assert "organizations" in Community.relations
    assert Community.relations.organizations


def test_community_organizations_validation(
    app, db, location, full_community, community_type_record
):
    comm = Community.create(full_community, slug="test")
    comm.commit()
    db.session.commit()

    # test it was saved properly
    aff = comm.metadata["organizations"][0]
    assert aff["name"] == "My Org"


def test_community_organizations_with_multiple_organizations(
    app, db, location, full_community, community_type_record
):
    community_copy = deepcopy(full_community)
    community_copy["metadata"]["organizations"].append({"name": "Another organization"})
    comm = Community.create(community_copy, slug="test")
    comm.commit()
    db.session.commit()

    aff_list = comm.metadata["organizations"]
    assert len(aff_list) == 2
    assert aff_list[0]["name"] == "My Org"
    assert aff_list[1]["name"] == "Another organization"


def test_community_organizations_with_name_cleanup_validation(
    app, db, location, affiliation, minimal_community
):
    """Creates a community with an existing affiliation."""
    slug = minimal_community.pop("slug")
    community_copy = deepcopy(minimal_community)
    community_copy["metadata"]["organizations"] = [{"id": "cern", "name": "CERN"}]
    comm = Community.create(community_copy, slug=slug)
    comm.commit()
    db.session.commit()

    # test it was saved properly
    aff = comm.metadata["organizations"][0]
    # name is not retrieved since it is only used when dereferencing
    assert aff.get("id") == "cern"
    assert aff.get("name") is None


def test_community_organizations_indexing(
    app, db, affiliation, location, full_community, community_type_record
):
    community_copy = deepcopy(full_community)
    community_copy["metadata"]["organizations"].append({"id": "cern", "name": "CERN"})
    comm = Community.create(community_copy, slug="test").commit()
    db.session.commit()

    # Dump community - dumps will dereference relations.
    dump = comm.dumps()
    expected_organisations = [
        {"name": "My Org"},
        {
            "id": "cern",
            "name": "CERN",
            "@v": dump["metadata"]["organizations"][1]["@v"],
        },
    ]

    assert dump["metadata"]["organizations"] == expected_organisations

    # Load comm again - should produce an identical record.
    loaded_comm = Community.loads(dump)
    assert dict(comm) == dict(loaded_comm)

    # Calling commit() will clear the dereferenced relation.
    loaded_comm.commit()
    loaded_aff_list = loaded_comm["metadata"]["organizations"]
    assert len(loaded_aff_list) == 2
    assert loaded_aff_list[0] == {"name": "My Org"}
    assert loaded_aff_list[1] == {"id": "cern"}


def test_community_organizations_invalid(
    app, db, location, full_community, community_type_record
):
    """Should fail on invalid id's and invalid structure."""
    comunity_copy = deepcopy(full_community)
    # The id "invalid" does not exists.
    comunity_copy["metadata"]["organizations"] = [{"id": "invalid"}]
    pytest.raises(
        InvalidRelationValue, Community.create(comunity_copy, slug="test").commit
    )

    # Not a list of objects
    comunity_copy["metadata"]["organizations"] = {"id": "cern"}
    pytest.raises(ValidationError, Community.create, comunity_copy, slug="test")

    # no additional keys are allowed
    comunity_copy["metadata"]["organizations"] = [{"test": "cern"}]
    pytest.raises(ValidationError, Community.create, comunity_copy, slug="test")

    # non-string types are not allowed as id values
    comunity_copy["metadata"]["organizations"] = [{"id": 1}]
    pytest.raises(ValidationError, Community.create, comunity_copy, slug="test")

    # No duplicates
    comunity_copy["metadata"]["organizations"] = [{"id": "cern"}, {"id": "cern"}]
    pytest.raises(ValidationError, Community.create, comunity_copy, slug="test")
