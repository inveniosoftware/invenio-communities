# SPDX-FileCopyrightText: 2023-2026 CERN.
# SPDX-FileCopyrightText: 2024 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Test invenio-communities alembic."""

import pytest
from invenio_db.utils import alembic_test_context, drop_alembic_version_table


def test_alembic(base_app, database):
    """Test alembic recipes."""
    db = database
    ext = base_app.extensions["invenio-db"]

    if db.engine.name == "sqlite":
        raise pytest.skip("Upgrades are not supported on SQLite.")

    base_app.config["ALEMBIC_CONTEXT"] = alembic_test_context()

    # Check that this package's SQLAlchemy models have been properly registered
    tables = [x for x in db.metadata.tables]
    assert "communities_metadata" in tables
    assert "communities_members" in tables

    # Check that Alembic agrees that there's no further tables to create.
    assert len(ext.alembic.compare_metadata()) == 0

    # Drop everything and recreate tables all with Alembic
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()

    assert not ext.alembic.compare_metadata()

    drop_alembic_version_table()
