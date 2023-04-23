#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Update role_id type (downgrade recipe)."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "37b21951084c"
down_revision = "a3f5a8635cbb"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    op.alter_column(
        "communities_members",
        "group_id",
        existing_type=sa.String(length=80),
        type_=sa.INTEGER(),
        existing_nullable=True,
        postgresql_using="group_id::integer",
    )
    op.create_foreign_key(
        op.f("fk_communities_members_group_id_accounts_role"),
        "communities_members",
        "accounts_role",
        ["group_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.alter_column(
        "communities_archivedinvitations",
        "group_id",
        existing_type=sa.String(length=80),
        type_=sa.INTEGER(),
        existing_nullable=True,
        postgresql_using="group_id::integer",
    )
    op.create_foreign_key(
        op.f("fk_communities_archivedinvitations_group_id_accounts_role"),
        "communities_archivedinvitations",
        "accounts_role",
        ["group_id"],
        ["id"],
        ondelete="RESTRICT",
    )
