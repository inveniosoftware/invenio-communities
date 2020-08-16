# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community module tests."""

import uuid

import pytest
from flask import url_for
from invenio_accounts.testutils import create_test_user, login_user_via_session
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record

from invenio_communities.api import Community
from invenio_communities.indexer import CommunityIndexer


@pytest.fixture
def record(db, es, users):
    _, record_owner, _ = users
    record = Record.create({
        'title': 'Title',
        '_owners': [record_owner.id],
    })
    recid = PersistentIdentifier.create(
        pid_type='recid', pid_value='12345',
        object_uuid=record.id, object_type='rec',
        status='R')
    db.session.commit()
    RecordIndexer().index_by_id(str(record.id))
    yield recid, record


@pytest.fixture
def community(db, es, users):
    community_owner, _, _ = users
    community_id = str(uuid.uuid4())
    comid = PersistentIdentifier.create(
        pid_type='comid', pid_value='biosyslit',
        object_uuid=community_id, object_type='com',
        status='R')
    community = Community.create({
        'id': 'comm_id',
        'title': 'Title',
        'type': 'topic',
        'created_by': community_owner.id,
    }, id_=community_id)
    db.session.commit()
    CommunityIndexer().index_by_id(str(community.id))
    yield comid, community


def test_simple_flow(db, es_clear, community, record, client, users):
    """Test basics operations on records."""
    # TODO
    # /api/communities/<comid>/requests/records/
    comid, community = community
    recid, record = record
    _, record_owner, _ = users
    login_user_via_session(client, user=record_owner)
    community_records_list_url = url_for(
        'invenio_communities_records.requests_list', pid_value=comid.pid_value)
    resp = client.post(community_records_list_url, json={
        'pid': recid.pid_value,
        'record_pid': recid.pid_value,
    })

    # create

    # read

    # update

    # delete

    pass


def test_records_permissions(db, es_clear, community, record, client, users):
    """Test permissions on records."""
    # TODO
    pass


def test_records_validation(db, es_clear, community, record, client, users):
    """Test records validation."""
    # TODO
    pass


def test_records_search(db, es_clear, community, record, client, users):
    """Test records search."""
    # TODO
    pass
