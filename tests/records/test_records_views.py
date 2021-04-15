# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community module tests."""

import pytest
from flask import url_for
from invenio_accounts.testutils import login_user_via_session


@pytest.mark.skip()
def test_simple_flow(
        db, es_clear, community, record, client, record_owner,
        community_owner):
    """Test basics operations on records."""
    comid, community = community
    recid, record = record
    login_user_via_session(client, user=record_owner)
    community_records_list_url = url_for(
        'invenio_communities_records.community_records_list',
        pid_value=comid.pid_value)

    resp = client.post(community_records_list_url, json={
        'record_pid': recid.pid_value
    })
    assert resp.status_code == 201
    community_record_links = resp.json['links']
    community_record_id = resp.json['id']

    login_user_via_session(client, user=community_owner)
    resp = client.post(
        community_record_links['comment'],
        json={'message': 'Hello there'})
    assert resp.status_code == 201

    login_user_via_session(client, user=record_owner)
    resp = client.post(
        community_record_links['comment'],
        json={'message': 'Oh hi mark'})
    assert resp.status_code == 201

    login_user_via_session(client, user=community_owner)
    resp = client.get(community_record_links['self'])
    assert resp.status_code == 200

    resp = client.post(community_record_links['accept'])
    assert resp.status_code == 201

    login_user_via_session(client, user=record_owner)

    community_record_item_url = url_for(
        'invenio_communities_records.community_records_item',
        pid_value=comid.pid_value,
        community_record_id=community_record_id)

    resp = client.delete(community_record_item_url)
    assert resp.status_code == 204


@pytest.mark.skip()
def test_alternate_flow(
        db, es_clear, community, record, client, record_owner,
        community_owner):
    """Test basics operations on records."""
    comid, community = community
    recid, record = record
    login_user_via_session(client, user=community_owner)
    community_records_list_url = url_for(
        'invenio_communities_records.community_records_list',
        pid_value=comid.pid_value)

    resp = client.post(community_records_list_url, json={
        'record_pid': recid.pid_value
    })
    assert resp.status_code == 201
    community_record_links = resp.json['links']
    community_record_id = resp.json['id']

    login_user_via_session(client, user=record_owner)
    resp = client.post(
        community_record_links['comment'],
        json={'message': 'Hello there'})
    assert resp.status_code == 201

    login_user_via_session(client, user=community_owner)
    resp = client.post(
        community_record_links['comment'],
        json={'message': 'Oh hi mark'})
    assert resp.status_code == 201

    login_user_via_session(client, user=record_owner)
    resp = client.get(community_record_links['self'])
    assert resp.status_code == 200

    resp = client.post(community_record_links['accept'])
    assert resp.status_code == 201

    login_user_via_session(client, user=community_owner)

    community_record_item_url = url_for(
        'invenio_communities_records.community_records_item',
        pid_value=comid.pid_value,
        community_record_id=community_record_id)

    resp = client.delete(community_record_item_url)
    assert resp.status_code == 204




@pytest.mark.skip()
def test_records_permissions(db, es_clear, community, record, client, users):
    """Test permissions on records."""
    # TODO
    pass


@pytest.mark.skip()
def test_records_validation(db, es_clear, community, record, client, users):
    """Test records validation."""
    # TODO
    pass


@pytest.mark.skip()
def test_records_search(db, es_clear, community, record, client, users):
    """Test records search."""
    # TODO
    pass
