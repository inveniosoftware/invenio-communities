# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2023 TU Wien.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Communities user moderation actions."""

from invenio_access.permissions import Identity, system_identity
from invenio_db import db
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.uow import TaskOp
from invenio_search.api import RecordsSearchV2
from invenio_search.engine import dsl
from invenio_vocabularies.proxies import current_service as vocab_service

from invenio_communities.proxies import current_communities

from .tasks import delete_community, restore_community


def get_user_communities(user_id, from_db=False):
    """Helper function for getting all communities with the user as the sole owner."""
    mem_cls = current_communities.service.members.record_cls
    mem_model_cls = mem_cls.model_cls

    if from_db:
        query = db.session.query(mem_model_cls.community_id).filter(
            mem_model_cls.user_id == user_id,
            mem_model_cls.role == "owner",
        )
        return (row[0] for row in query.yield_per(1000))
    else:
        search = (
            RecordsSearchV2(index=mem_cls.index._name)
            .filter("term", user_id=user_id)
            .filter("term", role="owner")
            .source(["community_id"])
        )
        return (hit["community_id"] for hit in search.scan())


def on_block(user_id, uow=None, **kwargs):
    """Removes records that belong to a user.

    Note: This function operates on all records of a user and thus has the potential
    to be a very heavy operation! Thus it should not be called as part of the handling
    of an HTTP request!
    """
    user_id = str(user_id)
    tombstone_data = {"note": _("User was blocked")}

    # set the removal reason if the vocabulary item exists
    try:
        removal_reason_id = kwargs.get("removal_reason_id", "misconduct")
        vocab = vocab_service.read(
            identity=system_identity, id_=("removalreasons", removal_reason_id)
        )
        tombstone_data["removal_reason"] = {"id": vocab.id}
    except PIDDoesNotExistError:
        pass

    for comm in get_user_communities(user_id):
        uow.register(
            TaskOp(
                delete_community,
                pid=comm.pid.pid_value,
                tombstone_data=tombstone_data,
            )
        )


def on_restore(user_id, uow=None, **kwargs):
    """Restores records that belong to a user.

    Note: This function operates on all records of a user and thus has the potential
    to be a very heavy operation! Thus it should not be called as part of the handling
    of an HTTP request!
    """
    user_id = str(user_id)

    # restore all the deleted records of that user
    for comm in get_user_communities(user_id):
        uow.register(TaskOp(restore_community, pid=comm.pid.pid_value))


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
