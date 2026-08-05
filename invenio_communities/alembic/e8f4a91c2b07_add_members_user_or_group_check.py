# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Add missing check constraint on communities_members.

The model has always declared ``CheckConstraint(..., name="user_or_group")``
(rendered as ``ck_communities_members_user_or_group``), but no Alembic
revision created it. Alembic 1.19+ detects that drift in
``test_alembic`` consumers such as invenio-rdm-records.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "e8f4a91c2b07"
down_revision = "1777209602"
branch_labels = ()
depends_on = None

_CONSTRAINT_NAME = "ck_communities_members_user_or_group"
_TABLE = "communities_members"
_SQL = (
    "(user_id IS NULL AND group_id IS NOT NULL) OR "
    "(user_id IS NOT NULL AND group_id IS NULL)"
)


def upgrade():
    """Upgrade database."""
    op.create_check_constraint(_CONSTRAINT_NAME, _TABLE, _SQL)


def downgrade():
    """Downgrade database."""
    op.drop_constraint(_CONSTRAINT_NAME, _TABLE, type_="check")
