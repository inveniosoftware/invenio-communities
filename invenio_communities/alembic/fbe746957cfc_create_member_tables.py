#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create member tables"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = 'fbe746957cfc'
down_revision = 'f701a32e6fbe'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column(
        'communities_members',
        sa.Column('active', sa.Boolean(), nullable=False))
    op.add_column(
        'communities_members',
        sa.Column('visible', sa.Boolean(), nullable=False))
    op.add_column(
        'communities_members',
        sa.Column('group_id', sa.Integer(), nullable=True))
    op.add_column(
        'communities_members',
        sa.Column('request_id', UUIDType(), nullable=True))
    op.create_index(
        op.f('ix_communities_members_active'),
        'communities_members',
        ['active'],
        unique=False
    )
    op.create_index(
        'ix_community_group',
        'communities_members',
        ['community_id', 'group_id'],
        unique=True
    )
    op.create_unique_constraint(
        op.f('uq_communities_members_request_id'),
        'communities_members',
        ['request_id']
    )
    op.drop_constraint(
        'fk_communities_members_user_id_accounts_user',
        'communities_members',
        type_='foreignkey'
    )
    op.create_foreign_key(
        op.f('fk_communities_members_user_id_accounts_user'),
        'communities_members', 'accounts_user', ['user_id'], ['id'],
        ondelete='RESTRICT'
    )
    op.create_foreign_key(
        op.f('fk_communities_members_group_id_accounts_role'),
        'communities_members', 'accounts_role', ['group_id'], ['id'],
        ondelete='RESTRICT'
    )
    op.create_foreign_key(
        op.f('fk_communities_members_request_id_request_metadata'),
        'communities_members', 'request_metadata', ['request_id'], ['id'],
        ondelete='SET NULL'
    )



def downgrade():
    """Downgrade database."""
    op.drop_constraint(op.f('fk_communities_members_request_id_request_metadata'), 'communities_members', type_='foreignkey')
    op.drop_constraint(op.f('fk_communities_members_group_id_accounts_role'), 'communities_members', type_='foreignkey')
    op.drop_constraint(op.f('fk_communities_members_user_id_accounts_user'), 'communities_members', type_='foreignkey')
    op.create_foreign_key('fk_communities_members_user_id_accounts_user', 'communities_members', 'accounts_user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(op.f('uq_communities_members_request_id'), 'communities_members', type_='unique')
    op.drop_index('ix_community_group', table_name='communities_members')
    op.drop_index(op.f('ix_communities_members_active'), table_name='communities_members')
    op.drop_column('communities_members', 'request_id')
    op.drop_column('communities_members', 'group_id')
    op.drop_column('communities_members', 'visible')
    op.drop_column('communities_members', 'active')
