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
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import (
    PIDAlreadyExists,
    PIDDeletedError,
    PIDDoesNotExistError,
)
from invenio_records_resources.services.uow import RecordIndexOp, unit_of_work
from invenio_search.engine import dsl

from ..proxies import current_communities


@shared_task
def create_demo_community(data, logo_path=None, feature=False):
    """Create a demo community."""
    service = current_communities.service
    try:
        community = service.create(data=data, identity=system_identity)

        # upload logo for community if provided
        if logo_path:
            with open(logo_path, "rb") as filestream:
                service.update_logo(system_identity, community.id, filestream)

        if feature:
            featured_data = {"start_date": datetime.utcnow().isoformat()}
            service.featured_create(system_identity, community.id, featured_data)

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
        extra_filter=dsl.Q("range", **{"featured.future": {"lte": now}}),
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
