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
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record

from invenio_communities.api import Community
from invenio_communities.indexer import CommunityIndexer

# PID + RecordMetadata

# comid:biobyslist <-> recid:12345

# @pytest.fixture
# def record(db, es):
#     record = Record.create({
#         'title': 'Title',
#     })
#     recid = PersistentIdentifier.create(
#         pid_type='recid', pid_value='12345',
#         object_uuid=record.id, object_type='rec')
#     db.session.commit()
#     RecordIndexer().index_by_id(str(record.id))
#     yield recid, record


# @pytest.fixture
# def community(db, es):
#     community = Community.create(id_=uuid.uuid4(), {
#         'title': 'Title',
#     })
#     comid = PersistentIdentifier.create(
#         pid_type='comid', pid_value='biosyslit',
#         object_uuid=community.id, object_type='com')
#     db.session.commit()
#     CommunityIndexer().index_by_id(str(community.id))
#     yield comid, community

# # test create record
# def test_inclusion_request(client, community, record, users):
#     """Test record creation."""
#     # /api/communities/<comid>/requests/records/
#     community_records_list_url = url_for('invenio_communities_records.requests_list')
#     resp = client.post(community_records_list_url, json={
#         'pid': '12345',
#         # 'pid': 'foo',
#     })
# # test delete record
