# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Create communities members table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy_utils import types

# revision identifiers, used by Alembic.
revision = 'a0f01ee61a5f'
down_revision = 'de9c14cbb0b2'
branch_labels = ()
depends_on = ["9848d0149abd"]


def upgrade():
    """Upgrade database."""
    op.create_table('communities_members',
        sa.Column(
            'created',
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'),
            nullable=False
        ),
        sa.Column(
            'updated',
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'),
            nullable=False
        ),
        sa.Column(
            'json',
            sa.JSON()
                .with_variant(types.json.JSONType(), 'mysql')
                .with_variant(
                    postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
                    'postgresql'
                )
                .with_variant(types.json.JSONType(), 'sqlite'),
            nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('id', types.uuid.UUIDType(), nullable=False),
        sa.Column('community_id', types.uuid.UUIDType(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ['community_id'],
            ['communities_metadata.id'],
            name=op.f(
                'fk_communities_members_community_id_communities_metadata'
            ),
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['accounts_user.id'],
            name=op.f(
                'fk_communities_members_user_id_accounts_user'
            ),
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_communities_members'))
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('communities_members')
