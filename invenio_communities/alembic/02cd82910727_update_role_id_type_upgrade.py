#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Update role_id type.

This recipe only contains the upgrade because as it directly depends on invenio-accounts recipe. That recipe is in
charge of deleting all the constraints on the role_id, including foreign keys using the role_id declared in this module.
Therefore, when in order to downgrade we need to split the recipes to be able to first execute the recipe in
invenio-access (f9843093f686) - this will invoke the recipe from invenio-accounts and delete all the FKs - and after
that we can execute the downgrade recipe (37b21951084c).
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "02cd82910727"
down_revision = (
    "f9843093f686",
    "37b21951084c",
)  # Depends on invenio-access revision id (f9843093f686)
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    # Foreign keys are already dropped by invenio-accounts
    op.alter_column(
        "communities_archivedinvitations",
        "group_id",
        existing_type=sa.INTEGER(),
        type_=sa.String(length=80),
        existing_nullable=True,
    )
    op.create_foreign_key(
        op.f("fk_communities_archivedinvitations_group_id_accounts_role"),
        "communities_archivedinvitations",
        "accounts_role",
        ["group_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.alter_column(
        "communities_members",
        "group_id",
        existing_type=sa.INTEGER(),
        type_=sa.String(length=80),
        existing_nullable=True,
    )
    op.create_foreign_key(
        op.f("fk_communities_members_group_id_accounts_role"),
        "communities_members",
        "accounts_role",
        ["group_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade():
    """Downgrade database."""
    pass
