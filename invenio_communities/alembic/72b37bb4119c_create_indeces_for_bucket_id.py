#
# This file is part of Invenio.
# Copyright (C) 2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create indeces for bucket_id."""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "72b37bb4119c"
down_revision = "5c68d45c80f0"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_index(
        op.f("ix_communities_metadata_bucket_id"),
        "communities_metadata",
        ["bucket_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_communities_files_object_version_id"),
        "communities_files",
        ["object_version_id"],
        unique=False,
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(
        op.f("ix_communities_metadata_bucket_id"), table_name="communities_metadata"
    )
    op.drop_index(
        op.f("ix_communities_files_object_version_id"), table_name="communities_files"
    )
