# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Field context."""

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
        return self.field._m2m_model_class.query.filter(community_id=community_or_id)
