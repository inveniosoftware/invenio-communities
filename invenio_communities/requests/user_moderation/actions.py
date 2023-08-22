# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Communities user moderation actions."""

from invenio_access.permissions import Identity, system_identity
from invenio_records_resources.services.uow import RecordIndexOp, unit_of_work
from invenio_search.engine import dsl

from invenio_communities.proxies import current_communities


def on_block(user_id, uow=None, **kwargs):
    """Removes communities that belong to a user."""
    pass


def on_restore(user_id, uow=None, **kwargs):
    """Restores communities that belong to a user."""
    pass


def on_approve(user_id, uow=None, **kwargs):
    """Execute on user approve.

    Re-index user records and dump verified field into records.
    """
    # import here due to circular import
    from invenio_communities.members.records.api import Member

    user_owned_communities = [
        m[0] for m in Member.get_memberships(Identity(user_id)) if m[1] == "owner"
    ]
    communities_filter = dsl.Q(
        "terms", **{"id": [id_ for id_ in user_owned_communities]}
    )
    community_service = current_communities.service
    community_service.reindex(system_identity, extra_filter=communities_filter)
