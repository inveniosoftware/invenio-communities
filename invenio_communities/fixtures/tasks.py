# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
