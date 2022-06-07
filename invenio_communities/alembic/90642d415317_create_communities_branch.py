# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
