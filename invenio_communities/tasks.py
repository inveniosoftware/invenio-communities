# SPDX-FileCopyrightText: 2023-2024 CERN.
# SPDX-License-Identifier: MIT

"""Invenio communities tasks."""

from celery import shared_task

from invenio_communities.proxies import current_identities_cache


@shared_task
def clear_cache():
    """Clears the cache.

    This is meant to be used to delete the community caches that contain the identity id of the users.
    """
    current_identities_cache.flush()
