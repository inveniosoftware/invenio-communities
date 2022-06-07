#
# This file is part of Invenio.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create communities members table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy_utils.types import JSONType, UUIDType

# revision identifiers, used by Alembic.
revision = "f701a32e6fbe"
down_revision = "de9c14cbb0b2"
branch_labels = ()
depends_on = "9848d0149abd"


def upgrade():
    """Upgrade database."""
    op.create_table(
        "communities_members",
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
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("id", UUIDType(), nullable=False),
        sa.Column("community_id", UUIDType(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["communities_metadata.id"],
            name=op.f("fk_communities_members_community_id_communities_metadata"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["accounts_user.id"],
            name=op.f("fk_communities_members_user_id_accounts_user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_communities_members")),
    )
    op.create_index(
        "ix_community_user",
        "communities_members",
        ["community_id", "user_id"],
        unique=True,
    )


def downgrade():
    """Downgrade database."""
    op.drop_index("ix_community_user", table_name="communities_members")
    op.drop_table("communities_members")
