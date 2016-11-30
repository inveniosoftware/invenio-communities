#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Renaming foreign keys in communities."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '653a857d84c9'
down_revision = '2d9884d0e3fa'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    # create new columns
    op.add_column(
        'communities_community',
        sa.Column('user_id', sa.Integer()))
    op.add_column(
        'communities_community_record',
        sa.Column('community_id', sa.String(length=100)))
    op.add_column(
        'communities_community_record',
        sa.Column('record_id',
                  sqlalchemy_utils.types.uuid.UUIDType()))
    op.add_column(
        'communities_community_record',
        sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column(
        'communities_featured_community',
        sa.Column('community_id', sa.String(length=100)))

    # drop foreign keys
    op.execute('COMMIT')  # See https://bitbucket.org/zzzeek/alembic/issue/123
    ctx = op.get_context()
    insp = Inspector.from_engine(ctx.connection.engine)

    for table_name, referred_tables in (
            ('communities_community', {'accounts_user', }),
            ('communities_community_record', {
                'records_metadata', 'accounts_user', 'communities_community'}),
            ('communities_featured_community', {'communities_community', })):
        for fk in insp.get_foreign_keys(table_name):
            if fk['referred_table'] in referred_tables:
                op.drop_constraint(
                    op.f(fk['name']), table_name, type_='foreignkey'
                )

    communities_community = sa.table(
        'communities_community',
        sa.column('user_id', sa.Integer),
        sa.column('id_user', sa.Integer),
    )
    op.execute(communities_community.update().values(
        user_id=communities_community.c.id_user
    ))

    communities_community_record = sa.table(
        'communities_community_record',
        sa.column('community_id', sa.String),
        sa.column('id_community', sa.String),
        sa.column('record_id',
                  sqlalchemy_utils.types.uuid.UUIDType),
        sa.column('id_record',
                  sqlalchemy_utils.types.uuid.UUIDType),
        sa.column('user_id', sa.Integer),
        sa.column('id_user', sa.Integer),
    )
    op.execute(communities_community_record.update().values(
        community_id=communities_community_record.c.id_community,
        record_id=communities_community_record.c.id_record,
        user_id=communities_community_record.c.id_user,
    ))

    communities_featured_community = sa.table(
        'communities_featured_community',
        sa.column('community_id', sa.String),
        sa.column('id_community', sa.String),
    )
    op.execute(communities_featured_community.update().values(
        community_id=communities_featured_community.c.id_community,
    ))

    # disable initially allowed null values
    op.alter_column('communities_community', 'user_id',
                    existing_type=sa.Integer(), nullable=False)
    op.alter_column('communities_community_record', 'community_id',
                    existing_type=sa.String(length=100), nullable=False)
    op.alter_column('communities_community_record', 'record_id',
                    existing_type=sqlalchemy_utils.types.uuid.UUIDType(),
                    nullable=False)
    op.alter_column('communities_featured_community', 'community_id',
                    existing_type=sa.String(length=100), nullable=False)

    # create new foreign keys
    op.create_foreign_key(
        None, 'communities_community', 'accounts_user',
        ['user_id'], ['id'])
    op.create_foreign_key(
        None, 'communities_community_record', 'records_metadata',
        ['record_id'], ['id'])
    op.create_foreign_key(
        None, 'communities_community_record', 'accounts_user',
        ['user_id'], ['id'])
    op.create_foreign_key(
        None, 'communities_community_record', 'communities_community',
        ['community_id'], ['id'])
    op.create_foreign_key(
        None, 'communities_featured_community', 'communities_community',
        ['community_id'], ['id'])

    # everything is moved so we can drop the old columns
    op.drop_column('communities_community', 'id_user')
    op.drop_column('communities_community_record', 'id_record')
    op.drop_column('communities_community_record', 'id_user')
    op.drop_column('communities_community_record', 'id_community')
    op.drop_column('communities_featured_community', 'id_community')


def downgrade():
    """Downgrade database."""
    # create new columns
    op.add_column(
        'communities_community',
        sa.Column('id_user', sa.Integer()))
    op.add_column(
        'communities_community_record',
        sa.Column('id_community', sa.String(length=100)))
    op.add_column(
        'communities_community_record',
        sa.Column('id_record',
                  sqlalchemy_utils.types.uuid.UUIDType()))
    op.add_column(
        'communities_community_record',
        sa.Column('id_user', sa.Integer(), nullable=True))
    op.add_column(
        'communities_featured_community',
        sa.Column('id_community', sa.String(length=100)))

    # drop foreign keys
    op.execute('COMMIT')  # See https://bitbucket.org/zzzeek/alembic/issue/123
    ctx = op.get_context()
    insp = Inspector.from_engine(ctx.connection.engine)

    for table_name, referred_tables in (
            ('communities_community', {'accounts_user', }),
            ('communities_community_record', {
                'records_metadata', 'accounts_user', 'communities_community'}),
            ('communities_featured_community', {'communities_community', })):
        for fk in insp.get_foreign_keys(table_name):
            if fk['referred_table'] in referred_tables:
                op.drop_constraint(
                    op.f(fk['name']), table_name, type_='foreignkey'
                )

    communities_community = sa.table(
        'communities_community',
        sa.column('id_user', sa.Integer),
        sa.column('user_id', sa.Integer),
    )
    op.execute(communities_community.update().values(
        id_user=communities_community.c.user_id
    ))

    communities_community_record = sa.table(
        'communities_community_record',
        sa.column('id_community', sa.String),
        sa.column('community_id', sa.String),
        sa.column('id_record',
                  sqlalchemy_utils.types.uuid.UUIDType),
        sa.column('record_id',
                  sqlalchemy_utils.types.uuid.UUIDType),
        sa.column('id_user', sa.Integer),
        sa.column('user_id', sa.Integer),
    )
    op.execute(communities_community_record.update().values(
        id_community=communities_community_record.c.community_id,
        id_record=communities_community_record.c.record_id,
        id_user=communities_community_record.c.user_id,
    ))

    communities_featured_community = sa.table(
        'communities_featured_community',
        sa.column('id_community', sa.String),
        sa.column('community_id', sa.String),
    )
    op.execute(communities_featured_community.update().values(
        id_community=communities_featured_community.c.community_id,
    ))

    # disable initially allowed null values
    op.alter_column('communities_community', 'id_user',
                    existing_type=sa.Integer(), nullable=False)
    op.alter_column('communities_community_record', 'id_community',
                    existing_type=sa.String(length=100), nullable=False)
    op.alter_column('communities_community_record', 'id_record',
                    existing_type=sqlalchemy_utils.types.uuid.UUIDType(),
                    nullable=False)
    op.alter_column('communities_featured_community', 'id_community',
                    existing_type=sa.String(length=100), nullable=False)

    # create new foreign keys
    op.create_foreign_key(
        None, 'communities_community', 'accounts_user',
        ['id_user'], ['id'])
    op.create_foreign_key(
        None, 'communities_community_record', 'records_metadata',
        ['id_record'], ['id'])
    op.create_foreign_key(
        None, 'communities_community_record', 'accounts_user',
        ['id_user'], ['id'])
    op.create_foreign_key(
        None, 'communities_community_record', 'communities_community',
        ['id_community'], ['id'])
    op.create_foreign_key(
        None, 'communities_featured_community', 'communities_community',
        ['id_community'], ['id'])

    # everything is moved so we can drop the old columns
    op.drop_column('communities_community', 'user_id')
    op.drop_column('communities_community_record', 'record_id')
    op.drop_column('communities_community_record', 'user_id')
    op.drop_column('communities_community_record', 'community_id')
    op.drop_column('communities_featured_community', 'community_id')
