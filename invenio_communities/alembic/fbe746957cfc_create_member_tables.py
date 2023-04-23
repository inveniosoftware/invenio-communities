#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create member tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy_utils import JSONType, UUIDType

# revision identifiers, used by Alembic.
revision = "fbe746957cfc"
down_revision = "f701a32e6fbe"
branch_labels = ()
depends_on = (
    "a14fa442680f",
    "2f63be7b7572",
)  # where the accounts_role and request_metadata table are created


def upgrade():
    """Upgrade database."""
    op.add_column(
        "communities_members", sa.Column("active", sa.Boolean(), nullable=False)
    )
    op.add_column(
        "communities_members", sa.Column("visible", sa.Boolean(), nullable=False)
    )
    op.add_column(
        "communities_members", sa.Column("group_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "communities_members", sa.Column("request_id", UUIDType(), nullable=True)
    )
    op.create_index(
        op.f("ix_communities_members_active"),
        "communities_members",
        ["active"],
        unique=False,
    )
    op.create_index(
        "ix_community_group",
        "communities_members",
        ["community_id", "group_id"],
        unique=True,
    )
    op.create_unique_constraint(
        op.f("uq_communities_members_request_id"), "communities_members", ["request_id"]
    )
    op.drop_constraint(
        "fk_communities_members_user_id_accounts_user",
        "communities_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_communities_members_user_id_accounts_user"),
        "communities_members",
        "accounts_user",
        ["user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        op.f("fk_communities_members_group_id_accounts_role"),
        "communities_members",
        "accounts_role",
        ["group_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        op.f("fk_communities_members_request_id_request_metadata"),
        "communities_members",
        "request_metadata",
        ["request_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "communities_archivedinvitations",
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
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("visible", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("community_id", UUIDType(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("request_id", UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["communities_metadata.id"],
            name=op.f(
                "fk_communities_archivedinvitations_community_id_communities_metadata"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["accounts_role.id"],
            name=op.f("fk_communities_archivedinvitations_group_id_accounts_role"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["request_metadata.id"],
            name=op.f("fk_communities_archivedinvitations_request_id_request_metadata"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["accounts_user.id"],
            name=op.f("fk_communities_archivedinvitations_user_id_accounts_user"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_communities_archivedinvitations")),
        sa.UniqueConstraint(
            "request_id", name=op.f("uq_communities_archivedinvitations_request_id")
        ),
    )

    op.create_index(
        op.f("ix_communities_archivedinvitations_active"),
        "communities_archivedinvitations",
        ["active"],
        unique=False,
    )


def downgrade():
    """Downgrade database."""
    op.drop_constraint(
        op.f("fk_communities_members_request_id_request_metadata"),
        "communities_members",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_communities_members_group_id_accounts_role"),
        "communities_members",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_communities_members_user_id_accounts_user"),
        "communities_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_communities_members_user_id_accounts_user",
        "communities_members",
        "accounts_user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        op.f("uq_communities_members_request_id"), "communities_members", type_="unique"
    )
    op.drop_index("ix_community_group", table_name="communities_members")
    op.drop_index(
        op.f("ix_communities_members_active"), table_name="communities_members"
    )
    op.drop_column("communities_members", "request_id")
    op.drop_column("communities_members", "group_id")
    op.drop_column("communities_members", "visible")
    op.drop_column("communities_members", "active")

    op.drop_index(
        op.f("ix_communities_archivedinvitations_active"),
        table_name="communities_archivedinvitations",
    )
    op.drop_table("communities_archivedinvitations")
