# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Field context."""

from invenio_db import db
from invenio_records.systemfields import SystemFieldContext


class CommunitiesFieldContext(SystemFieldContext):
    """Context for communities field.

    This class implements the class-level methods available on a
    CommunitiesField. I.e. when you access the field through the class, for
    instance:

    .. code-block:: python

        Record.communities.query_by_community(community)
    """

    def query_by_community(self, community_or_id):
        """Query community-record relations for a given community."""
        return db.session.query(self.field._m2m_model_class).filter(
            community_id=community_or_id
        )
