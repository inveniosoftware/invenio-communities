# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_app.factory import create_api
from invenio_indexer.api import RecordIndexer
from mock_module.api import MockRecord


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_db.model": [
            "mock_module = mock_module.models",
        ],
        "invenio_jsonschemas.schemas": [
            "mock_module = mock_module.jsonschemas",
        ],
        "invenio_search.mappings": [
            "mocks = mock_module.mappings",
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=MockRecord, record_to_index=lambda r: (r.index._name, "_doc")
    )
