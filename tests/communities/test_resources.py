# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community module tests."""

import copy
import json
import pytest

from flask import url_for
from invenio_communities.communities.records.api import Community

# def assert_error_resp(res, expected_errors, expected_status_code=400):
#     """Assert errors in a client response."""
#     assert res.status_code == expected_status_code
#     payload = res.json
#     errors = payload.get('errors', [])
#     for field, msg in expected_errors:
#         if not field:  # top-level "message" error
#             assert msg in payload['message'].lower()
#             continue
#         assert any(
#             e['field'] == field and msg in e['message'].lower()
#             for e in errors), payload


# def create_test_community(client, user, data):
#     """Create test community."""
#     login_user_via_session(client, user=user)
#     list_url = url_for('invenio_records_rest.comid_list')
#     resp = client.post(list_url, json=data)
#     assert resp.status_code == 201
#     return resp


# def logout_user_session(client):
#     """Logout a user from the Flask test client session."""
#     with client.session_transaction() as sess:
#         del sess['user_id']


def _assert_single_item_response(response):
    """Assert the fields present on a single item response."""
    response_fields = response.json.keys()
    fields_to_check = [
        'created', 'id', 'links', 'metadata', 'updated'
    ]

    for field in fields_to_check:
        assert field in response_fields


def test_simple_flow(
    app, client_with_login, location, minimal_community_record, headers,
    es_clear
):
    client = client_with_login
    """Test a simple REST API flow."""
    # Create a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record))
    assert res.status_code == 201
    _assert_single_item_response(res)

    created_community = res.json
    id_ = created_community["id"]

    # Read the community
    res = client.get(f'/communities/{id_}', headers=headers)
    assert res.status_code == 200
    assert res.json['metadata'] == \
        created_community['metadata']

    read_community = res.json

    Community.index.refresh()

    # Search for created commmunity
    res = client.get(
        f'/communities', query_string={'q': f'id:{id_}'}, headers=headers)
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1
    assert res.json['hits']['hits'][0]['metadata'] == \
        created_community['metadata']

    # Update community
    data = copy.deepcopy(read_community)
    data["metadata"]["title"] = 'New title'

    res = client.put(
        f'/communities/{id_}', headers=headers, data=json.dumps(data))
    assert res.status_code == 200
    assert res.json['metadata']["title"] == 'New title'

    updated_community = res.json

    Community.index.refresh()

    # Search for updated commmunity
    res = client.get(
        f'/communities', query_string={'q': f'id:{id_}'}, headers=headers)
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1
    assert res.json['hits']['hits'][0]['metadata'] == \
        updated_community['metadata']
    data = res.json['hits']['hits'][0]
    assert updated_community['metadata']['title'] == 'New title'

    # Delete community
    res = client.delete(f'/communities/{id_}', headers=headers)
    assert res.status_code == 204

    # Read again community should give back 404
    res = client.get(f'/communities/{id_}', headers=headers)
    assert res.status_code == 410
    assert res.json["message"] == "The record has been deleted."
