# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Users-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio communities tasks."""
from celery import shared_task

from invenio_communities.proxies import current_identities_cache


@shared_task
def clear_cache():
    """Clears the cache.

    This is meant to be used to delete the community caches that contain the identity id of the users.
    """
    current_identities_cache.flush()
