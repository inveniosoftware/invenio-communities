#
# This file is part of Invenio.
# Copyright (C) 2016-2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add group notification preference to community members."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dfbc96c5211f"
down_revision = "5c68d45c80f0"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    # Add group_notification_enabled column to communities_members table
    # This column is nullable - NULL for user members, True/False for group members
    op.add_column(
        "communities_members",
        sa.Column("group_notification_enabled", sa.Boolean(), nullable=True),
    )

    # Set default value to True for existing group members (where group_id is not NULL)
    members_table = sa.sql.table(
        "communities_members",
        sa.sql.column("group_id"),
        sa.sql.column("group_notification_enabled"),
    )
    op.execute(
        members_table.update()
        .where(members_table.c.group_id.isnot(None))
        .values(group_notification_enabled=True)
    )

    # Add group_notification_enabled column to communities_archivedinvitations table
    op.add_column(
        "communities_archivedinvitations",
        sa.Column("group_notification_enabled", sa.Boolean(), nullable=True),
    )

    # Set default value to True for existing archived group invitations
    archived_table = sa.sql.table(
        "communities_archivedinvitations",
        sa.sql.column("group_id"),
        sa.sql.column("group_notification_enabled"),
    )
    op.execute(
        archived_table.update()
        .where(archived_table.c.group_id.isnot(None))
        .values(group_notification_enabled=True)
    )


def downgrade():
    """Downgrade database."""
    op.drop_column("communities_members", "group_notification_enabled")
    op.drop_column("communities_archivedinvitations", "group_notification_enabled")
