# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community module tests."""

from flask import url_for
from invenio_accounts.testutils import create_test_user, login_user_via_session
from invenio_search import current_search


def assert_error_resp(res, expected_errors, expected_status_code=400):
    """Assert errors in a client response."""
    assert res.status_code == expected_status_code
    payload = res.json
    errors = payload.get('errors', [])
    for field, msg in expected_errors:
        if not field:  # top-level "message" error
            assert msg in payload['message'].lower()
            continue
        assert any(
            e['field'] == field and msg in e['message'].lower()
            for e in errors), payload


def create_test_community(client, user, data):
    """Create test community."""
    login_user_via_session(client, user=user)
    list_url = url_for('invenio_records_rest.comid_list')
    resp = client.post(list_url, json=data)
    assert resp.status_code == 201
    return resp


def logout_user_session(client):
    """Logout a user from the Flask test client session."""
    with client.session_transaction() as sess:
        del sess['user_id']


def test_simple_flow(db, es_clear, client, users):
    """Test community minimal CRUD operations."""
    community_owner, _, _ = users
    list_url = url_for('invenio_records_rest.comid_list')
    login_user_via_session(client, user=community_owner)

    # Create
    resp = client.post(list_url, json={
        'id': 'minimal_comm',
        'title': 'Minimal community',
        'type': 'organization',
        'visibility': 'public',
    })

    assert resp.status_code == 201
    assert resp.json['metadata']['id'] == 'minimal_comm'
    assert resp.json['metadata']['title'] == 'Minimal community'
    assert resp.json['metadata']['type'] == 'organization'
    assert resp.json['links']['self'] == 'http://localhost/communities/minimal_comm'

    item_url = resp.json['links']['self']

    # Read
    resp = client.get(item_url)
    assert resp.status_code == 200
    assert resp.json['metadata']['id'] == 'minimal_comm'
    assert resp.json['metadata']['title'] == 'Minimal community'
    assert resp.json['metadata']['type'] == 'organization'
    assert resp.json['links']['self'] == 'http://localhost/communities/minimal_comm'

    # Update
    resp = client.put(item_url, json={
        'id': 'biosyslit',
        'title': 'Owner title',
        'type': 'organization',
        'visibility': 'public',
    })

    assert resp.status_code == 200
    assert resp.json['metadata']['title'] == 'Owner title'

    # Delete
    resp = client.delete(item_url)
    assert resp.status_code == 204

    logout_user_session(client)


def test_community_permissions(db, es_clear, client, users):
    """Test community CRUD operations."""
    # TODO: test for anonymous and regular user => not for owners
    community_owner, regular_user, _ = users
    list_url = url_for('invenio_records_rest.comid_list')

    # create demo community
    data = {
        'id': 'test_comm',
        'title': 'Testing community',
        'type': 'organization',
        'visibility': 'public',
    }
    resp = create_test_community(client, community_owner, data)
    item_url_owner = resp.json['links']['self']
    current_search.flush_and_refresh('communities')

    # ANONYMOUS
    logout_user_session(client)
    # create
    resp = client.post(list_url, json={
        'id': 'anonymous_comm',
        'title': 'Anonymous community',
        'type': 'organization',
        'visibility': 'public',
    })

    assert resp.status_code == 401

    # read
    resp = client.get(list_url)
    assert resp.status_code == 200
    assert resp.json['hits']['total'] == 1

    resp = client.get(item_url_owner)
    assert resp.status_code == 200
    assert resp.json['metadata']['title'] == 'Testing community'
    assert resp.json['metadata']['type'] == 'organization'
    assert resp.json['metadata']['id'] == 'test_comm'
    assert resp.json['links']['self'] == 'http://localhost/communities/test_comm'


    # update
    resp = client.put(item_url_owner, json={
        'id': 'biosyslit',
        'title': 'Owner title',
        'type': 'organization',
        'visibility': 'public',
    })

    assert resp.status_code == 401

    # delete
    resp = client.delete(item_url_owner)
    assert resp.status_code == 401

    # REGULAR USER
    login_user_via_session(client, user=regular_user)

    # create a community
    resp = client.post(list_url, json={
        'id': 'regular_comm',
        'title': 'Regular community',
        'type': 'organization',
        'visibility': 'public',
    })

    assert resp.status_code == 201
    assert resp.json['metadata']['id'] == 'regular_comm'
    assert resp.json['metadata']['title'] == 'Regular community'
    assert resp.json['metadata']['type'] == 'organization'
    assert resp.json['links']['self'] == 'http://localhost/communities/regular_comm'

    item_url_regular = resp.json['links']['self']
    current_search.flush_and_refresh('communities')

    # read
    resp = client.get(list_url)
    assert resp.status_code == 200
    assert resp.json['hits']['total'] == 2

    resp = client.get(item_url_regular)
    assert resp.status_code == 200
    assert resp.json['metadata']['id'] == 'regular_comm'
    assert resp.json['metadata']['title'] == 'Regular community'
    assert resp.json['metadata']['type'] == 'organization'
    assert resp.json['links']['self'] == 'http://localhost/communities/regular_comm'

    # update another community
    resp = client.put(item_url_owner, json={
        'id': 'biosyslit',
        'title': 'Regular title',
        'type': 'organization',
        'visibility': 'public',
    })

    assert resp.status_code == 403

    # Delete community
    resp = client.delete(item_url_owner)
    assert resp.status_code == 403

    # Logout
    logout_user_session(client)


def test_community_validation(db, es_clear, client, users):
    """Test community validation."""
    community_owner, regular_user, _ = users
    list_url = url_for('invenio_records_rest.comid_list')
    login_user_via_session(client, user=community_owner)

    # missing field
    resp = client.post(list_url, json={
        'id': 'biosyslit_val',
        'title': 'BLRval',
    })

    assert resp.status_code == 400
    assert resp.json['message'] == 'Validation error.'
    assert_error_resp(resp, (
        ('type', 'required field'),
    ))

    # wrong type field
    resp = client.post(list_url, json={
        'id': 'biosyslit_val',
        'title': 'BLRval',
        'type': 'wrong type'
    })

    assert resp.status_code == 400
    assert resp.json['message'] == 'Validation error.'
    assert_error_resp(resp, (
        ('type', 'must be one of'),
    ))

    # id already created
    resp = client.post(list_url, json={
        'id': 'comm_id',
        'title': 'Original title',
        'type': 'project'
    })

    assert resp.status_code == 201

    resp = client.post(list_url, json={
        'id': 'comm_id',
        'title': 'Duplicate title',
        'type': 'project'
    })

    assert resp.status_code == 400
    assert resp.json['message'] == 'Validation error.'
    assert_error_resp(resp, (
        ('id', 'is already assigned to a community'),
    ))

    # wrong domain
    resp = client.post(list_url, json={
        'id': 'domain_id',
        'title': 'Domain title',
        'type': 'project',
        'domains': ['wrong']
    })

    assert resp.status_code == 400
    assert resp.json['message'] == 'Validation error.'
    assert 'Must be one of' in resp.json['errors'][0]['message']

    # wrong domain formatting
    resp = client.post(list_url, json={
        'id': 'domain_id',
        'title': 'Domain title',
        'type': 'project',
        'domains': 'engineering'
    })

    assert resp.status_code == 400
    assert resp.json['message'] == 'Validation error.'
    assert_error_resp(resp, (
        ('domains', 'not a valid list'),
    ))

    # wrong field
    resp = client.post(list_url, json={
        'id': 'domain_id',
        'title': 'Domain title',
        'type': 'project',
        'field': 'wrong'
    })

    assert resp.status_code == 400
    assert resp.json['message'] == 'Validation error.'
    assert_error_resp(resp, (
        ('field', 'unknown field'),
    ))

    # test all fields
    resp = client.post(list_url, json={
        'id': 'full_comm',
        'title': 'All fields',
        'type': 'event',
        'curation_policy': 'Policy field',
        'page': 'Page field',
        'website': 'http://www.fullfield.com',
        'funding': ['OpenAire'],
        'domains': ['engineering', 'technology'],
        'verified': True,
        'visibility': 'public',
        'member_policy': 'open',
        'record_policy': 'open',
        'archived': 'False',
    })

    assert resp.status_code == 201


def test_community_search(db, es_clear, client, users):
    """Test community search."""


    community_owner, _ , _ = users
    list_url = url_for('invenio_records_rest.comid_list')
    login_user_via_session(client, user=community_owner)

    # creating demos communities
    resp = client.post(list_url, json={
        'id': 'regular_comm',
        'title': 'Regular community',
        'type': 'topic',
        'domains': ['engineering']
    })
    assert resp.status_code == 201

    resp = client.post(list_url, json={
        'id': 'biosyslit',
        'title': 'BLR',
        'type': 'topic',
        'domains': ['engineering', 'technology']
    })
    assert resp.status_code == 201

    current_search.flush_and_refresh('communities')

    # testing search
    resp = client.get(list_url, query_string={'q': 'title:BLR'})
    assert resp.status_code == 200
    assert resp.json['hits']['hits'][0]['metadata']['id'] == 'biosyslit'
    assert resp.json['hits']['hits'][0]['metadata']['title'] == 'BLR'
    assert resp.json['hits']['hits'][0]['metadata']['type'] == 'topic'
    assert resp.json['hits']['hits'][0]['links']['self'] == 'http://localhost/communities/biosyslit'

    resp = client.get(list_url, query_string={'type': 'topic'})
    assert resp.status_code == 200
    assert resp.json['hits']['total'] == 2

    resp = client.get(list_url, query_string={'domain': ['engineering']})
    assert resp.status_code == 200
    assert resp.json['hits']['total'] == 2
    resp = client.get(list_url, query_string={'domain': ['technology']})
    assert resp.status_code == 200
    assert resp.json['hits']['total'] == 1
