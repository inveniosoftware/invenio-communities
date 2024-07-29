# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""User moderation tasks."""

from celery import shared_task
from invenio_access.permissions import system_identity

from invenio_communities.errors import DeletionStatusError
from invenio_communities.proxies import current_communities


@shared_task(ignore_result=True)
def delete_community(community_id, tombstone_data):
    """Delete a single community."""
    try:
        current_communities.service.delete_community(
            system_identity, community_id, tombstone_data
        )
    except DeletionStatusError as ex:
        # Community is already deleted; index again to make sure search is up-to-date.
        current_communities.indexer.index(ex.community)


@shared_task(ignore_result=True)
def restore_community(community_id):
    """Restore a single community."""
    try:
        current_communities.service.restore_community(system_identity, community_id)
    except DeletionStatusError as ex:
        # Community is already restored; index again to make sure search is up-to-date.
        current_communities.indexer.index(ex.community)
