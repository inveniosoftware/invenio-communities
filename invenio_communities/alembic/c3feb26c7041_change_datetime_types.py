#
# This file is part of Invenio.
# Copyright (C) 2023 CERN.
# Copyright (C) 2026 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Alter datetime columns to utc aware datetime columns."""

from invenio_db.utils import (
    update_table_columns_column_type_to_datetime,
    update_table_columns_column_type_to_utc_datetime,
)

# revision identifiers, used by Alembic.
revision = "c3feb26c7041"
down_revision = "72b37bb4119c"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    for table_name in [
        "communities_metadata",
        "communities_files",
        "communities_members",
        "communities_featured",
        "communities_archivedinvitations",
    ]:
        update_table_columns_column_type_to_utc_datetime(table_name, "created")
        update_table_columns_column_type_to_utc_datetime(table_name, "updated")
    update_table_columns_column_type_to_utc_datetime(
        "communities_featured", "start_date"
    )


def downgrade():
    """Downgrade database."""
    for table_name in [
        "communities_metadata",
        "communities_files",
        "communities_members",
        "communities_featured",
        "communities_archivedinvitations",
    ]:
        update_table_columns_column_type_to_datetime(table_name, "created")
        update_table_columns_column_type_to_datetime(table_name, "updated")
    update_table_columns_column_type_to_datetime("communities_featured", "start_date")
