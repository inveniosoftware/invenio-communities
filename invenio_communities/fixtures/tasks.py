# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C)      2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for fixtures."""


from datetime import datetime

from celery import shared_task
from elasticsearch_dsl import Q
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import (
    PIDAlreadyExists,
    PIDDeletedError,
    PIDDoesNotExistError,
)
from invenio_records_resources.services.uow import RecordIndexOp, unit_of_work

from ..proxies import current_communities


@shared_task
def create_demo_community(data):
    """Create a demo community."""
    service = current_communities.service
    try:
        service.create(data=data, identity=system_identity)
    except PIDAlreadyExists:
        pass


@shared_task
def reindex_featured_entries():
    """Reindexes records having at least one future entry which is now in the past."""
    service = current_communities.service
    now = datetime.utcnow().isoformat()

    @unit_of_work()
    def reindex_community(hit, uow=None):
        community = service.record_cls.pid.resolve(hit["id"])
        uow.register(
            RecordIndexOp(community, indexer=service.indexer, index_refresh=True)
        )

    # using scan to get all communities
    record_list = service.scan(
        identity=system_identity,
        extra_filter=Q("range", **{"featured.future": {"lte": now}}),
    )
    for hit in record_list.hits:
        try:
            reindex_community(hit)
        # community has been renamed or deleted in the meantime.
        # will be reindexed in the service method.
        except PIDDoesNotExistError:
            pass
        except PIDDeletedError:
            pass
