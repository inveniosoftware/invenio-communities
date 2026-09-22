# SPDX-FileCopyrightText: 2022-2024 Graz University of Technology.
# SPDX-FileCopyrightText: 2022 Northwestern University.
# SPDX-License-Identifier: MIT

"""Test community schema.py."""

import copy

import pytest
from marshmallow import ValidationError

from invenio_communities.communities.schema import CommunitySchema

# Test CommunitySchema


def test_community_schema_filter_parent_id(app, minimal_community):
    schema = CommunitySchema()
    community_input = copy.deepcopy(minimal_community)

    # Case input has no parent, then dont add or do anything
    community_input.pop("parent", None)
    result = schema.load(community_input)
    assert "parent" not in result

    # Case input has empty parent, then keep parent with empty value
    community_input["parent"] = None
    result = schema.load(community_input)
    assert not result["parent"]
    community_input["parent"] = {}
    result = schema.load(community_input)
    assert not result["parent"]

    # Case input has dict parent with empty id, then raise validation error
    community_input["parent"] = {"foo": "foo"}
    with pytest.raises(
        ValidationError, match="Assigned parent community does not exist."
    ):
        result = schema.load(community_input)
    community_input["parent"]["id"] = None
    with pytest.raises(
        ValidationError, match="Assigned parent community does not exist."
    ):
        result = schema.load(community_input)

    # Case input has dict parent with non-empty non-string id
    community_input["parent"]["id"] = [1]
    with pytest.raises(
        ValidationError, match="Assigned parent community does not exist."
    ):
        result = schema.load(community_input)

    # Case input has dict parent with non-empty valid id
    community_input["parent"]["id"] = "some-potential-id"
    result = schema.load(community_input)
    assert {"id": "some-potential-id"} == result["parent"]

    # Case input has non-dict non-empty parent
    community_input["parent"] = "ignore me"
    result = schema.load(community_input)
    assert "parent" not in result
