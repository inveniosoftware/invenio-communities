# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for fixtures."""


from celery import shared_task
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDAlreadyExists

from ..proxies import current_communities


@shared_task
def create_demo_community(data):
    """Create a demo community."""
    service = current_communities.service
    try:
        service.create(data=data, identity=system_identity)
    except PIDAlreadyExists:
        pass
