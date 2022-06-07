#
# This file is part of Invenio.
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create featured communities table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = "5b478fe7ef7f"
down_revision = "fbe746957cfc"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        "communities_featured",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("community_id", UUIDType(), nullable=False),
        sa.Column(
            "start_date",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["communities_metadata.id"],
            name=op.f("fk_communities_featured_community_id_communities_metadata"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_communities_featured")),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table("communities_featured")
