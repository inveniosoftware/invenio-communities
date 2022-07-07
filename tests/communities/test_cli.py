# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the CLI."""

from faker import Faker

from invenio_communities.cli import (
    create_communities_custom_field,
    custom_field_exists_in_communities,
)
from invenio_communities.communities.records.api import Community
from invenio_communities.fixtures.demo import create_fake_community
from invenio_communities.fixtures.tasks import create_demo_community


def test_fake_demo_community_creation(
    app, db, location, search_clear, community_type_record
):
    """Assert that demo community creation works without failing."""
    faker = Faker()
    create_demo_community(create_fake_community(faker))


def test_create_communities_custom_fields(app, location, db, search_clear, cli_runner):
    """Assert that custom fields mappings are created for communities."""
    result = cli_runner(create_communities_custom_field, "-f", "mycommunityfield")
    assert result.exit_code == 0

    community_mapping_field = list(Community.index.get_mapping().values())[0][
        "mappings"
    ]["properties"]["custom_fields"]
    expected_value = {
        "properties": {
            "mycommunityfield": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            }
        }
    }
    assert community_mapping_field == expected_value

    # check for existence
    result = cli_runner(custom_field_exists_in_communities, "-f", "mycommunityfield")
    assert result.exit_code == 0
    assert "Field mycommunityfield exists" in result.output

    result = cli_runner(custom_field_exists_in_communities, "-f", "unknownfield")
    assert result.exit_code == 0
    assert "Field unknownfield does not exist" in result.output
