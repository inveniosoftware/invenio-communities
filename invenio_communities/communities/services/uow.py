# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Unit of work operations for featured community services."""

from invenio_db import db
from invenio_records_resources.services.uow import Operation


class CommunityFeaturedCommitOp(Operation):
    """Featured community add/update operation."""

    def __init__(self, featured_entry):
        """Initialize the commit operation."""
        super().__init__()
        self._featured_entry = featured_entry

    def on_register(self, uow):
        """Add to db session."""
        db.session.add(self._featured_entry)


class CommunityFeaturedDeleteOp(Operation):
    """OAI-PMH set delete operation."""

    def __init__(self, featured_entry):
        """Initialize the delete operation."""
        super().__init__()
        self._featured_entry = featured_entry

    def on_register(self, uow):
        """Delete entry."""
        db.session.delete(self._featured_entry)
