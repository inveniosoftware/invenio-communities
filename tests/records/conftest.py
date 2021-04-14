# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import uuid

import pytest
from invenio_accounts.testutils import create_test_user
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_communities.communities.records.api import Record


@pytest.fixture
def record_owner(db):
    """Record owner user."""
    yield create_test_user('record-owner@inveniosoftware.org')


@pytest.fixture
def record(db, es, record_owner):
    """Record fixture."""
    record = Record.create({
        'title': 'Title',
        '_owners': [record_owner.id],
    })
    recid = PersistentIdentifier.create(
        pid_type='recid', pid_value='12345',
        object_uuid=record.id, object_type='rec',
        status=PIDStatus.REGISTERED)
    db.session.commit()
    RecordIndexer().index_by_id(str(record.id))
    yield recid, record


# @pytest.fixture
# def accepted_community_record(db, es, community, record, record_owner):
#     """Community record fixture."""
#     comid, community = community
#     recid, record = record
#     # request = CommunityInclusionRequest.create(record_owner, id_=uuid.uuid4())
#     comm_record = CommunityRecord.create(record, recid, community, request)
#     comm_record.status = comm_record.Status.ACCEPTED
#     db.session.commit()
#     RecordIndexer().index_by_id(str(record.id))
#     yield comm_record
