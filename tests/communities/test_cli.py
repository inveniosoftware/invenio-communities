# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the CLI."""

from faker import Faker

from invenio_communities.fixtures.demo import create_fake_community
from invenio_communities.fixtures.tasks import create_demo_community


def test_fake_demo_community_creation(app, db, location, es_clear):
    """Assert that demo community creation works without failing."""
    faker = Faker()
    create_demo_community(create_fake_community(faker))
