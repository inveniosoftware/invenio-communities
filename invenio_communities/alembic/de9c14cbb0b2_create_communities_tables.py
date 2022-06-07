# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create communities tables."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import mysql, postgresql

# revision identifiers, used by Alembic.
revision = "de9c14cbb0b2"
down_revision = "90642d415317"
branch_labels = ()
depends_on = "8ae99b034410"


def upgrade():
    """Upgrade database."""
    op.create_table(
        "communities_metadata_version",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column(
            "bucket_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", "transaction_id", name=op.f("pk_communities_metadata_version")
        ),
    )
    op.create_index(
        op.f("ix_communities_metadata_version_end_transaction_id"),
        "communities_metadata_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_communities_metadata_version_operation_type"),
        "communities_metadata_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_communities_metadata_version_transaction_id"),
        "communities_metadata_version",
        ["transaction_id"],
        unique=False,
    )
    op.create_table(
        "communities_metadata",
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
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("bucket_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["bucket_id"],
            ["files_bucket.id"],
            name=op.f("fk_communities_metadata_bucket_id_files_bucket"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_communities_metadata")),
    )
    op.create_table(
        "communities_files",
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
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column(
            "key",
            sa.Text().with_variant(mysql.VARCHAR(length=255), "mysql"),
            nullable=False,
        ),
        sa.Column("record_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "object_version_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["object_version_id"],
            ["files_object.version_id"],
            name=op.f("fk_communities_files_object_version_id_files_object"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["record_id"],
            ["communities_metadata.id"],
            name=op.f("fk_communities_files_record_id_communities_metadata"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_communities_files")),
    )
    op.create_index(
        "uidx_communities_files_id_key", "communities_files", ["id", "key"], unique=True
    )


def downgrade():
    """Downgrade database."""
    op.drop_index("uidx_communities_files_id_key", table_name="communities_files")
    op.drop_table("communities_files")
    op.drop_table("communities_metadata")
    op.drop_index(
        op.f("ix_communities_metadata_version_transaction_id"),
        table_name="communities_metadata_version",
    )
    op.drop_index(
        op.f("ix_communities_metadata_version_operation_type"),
        table_name="communities_metadata_version",
    )
    op.drop_index(
        op.f("ix_communities_metadata_version_end_transaction_id"),
        table_name="communities_metadata_version",
    )
    op.drop_table("communities_metadata_version")
