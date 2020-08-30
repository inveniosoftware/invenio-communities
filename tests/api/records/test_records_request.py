# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community module tests."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


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
