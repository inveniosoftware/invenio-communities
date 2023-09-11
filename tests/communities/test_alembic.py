# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test alembic recipes for Invenio-RDM-Records."""

import pytest
from invenio_db.utils import alembic_test_context, drop_alembic_version_table

# Invenio-Vocabularies define an Alembic migration that include subjects and
# affiliations tables. The SQLAlchemy models are however not registered by
# default. This means that when alembic creates the database vs when SQLAlchemy
# creates the database there's a discrepancy. Importing the subjects model
# here, ensures the model get's registered, and we avoid the discrepancy.
from invenio_vocabularies.contrib.affiliations import models
from invenio_vocabularies.contrib.awards import models
from invenio_vocabularies.contrib.funders import models
from invenio_vocabularies.contrib.names import models
from invenio_vocabularies.contrib.subjects import models


@pytest.mark.skip(reason="Caused by mergepoint")
def test_alembic(base_app, database):
    """Test alembic recipes."""
    db = database
    ext = base_app.extensions["invenio-db"]

    if db.engine.name == "sqlite":
        raise pytest.skip("Upgrades are not supported on SQLite.")

    base_app.config["ALEMBIC_CONTEXT"] = alembic_test_context()

    # Check that this package's SQLAlchemy models have been properly registered
    tables = [x.name for x in db.get_tables_for_bind()]
    assert "communities_metadata" in tables
    assert "communities_files" in tables
    assert "communities_members" in tables
    assert "communities_featured" in tables

    # Check that Alembic agrees that there's no further tables to create.
    assert not ext.alembic.compare_metadata()

    # Hack to not having to deal with mock_metadata depending on which order
    # tests are run in.
    cmp_len = 2 if "mock_metadata" in tables else 0

    # Drop everything and recreate tables all with Alembic
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()
    assert len(ext.alembic.compare_metadata()) == cmp_len

    # Try to upgrade and downgrade
    ext.alembic.stamp()
    ext.alembic.downgrade(target="96e796392533")
    ext.alembic.upgrade()
    assert len(ext.alembic.compare_metadata()) == cmp_len

    drop_alembic_version_table()
