# SPDX-FileCopyrightText: 2016-2021 CERN.
# SPDX-License-Identifier: MIT

"""Create communities branch."""

# revision identifiers, used by Alembic.
revision = "90642d415317"
down_revision = None
branch_labels = ("invenio_communities",)
depends_on = "dbdbc1b19cf2"


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
