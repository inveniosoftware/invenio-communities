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


def _assert_optional_items_metadata(response):
    """Assert the fields present on the metadata """
    metadata_fields = response.json['metadata'].keys()
    fields_to_check = [
        "description", "type", "alternate_identifiers", "curation_policy",
        "page", "website", "domains", "funding", "award"
    ]

    for field in fields_to_check:
        assert field in metadata_fields


def test_simple_flow(
    app, client_with_login, location, minimal_community_record, headers,
    es_clear
):
    """Test a simple REST API flow."""
    client = client_with_login
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


def test_post_schema_validation(
    app, client_with_login, location, minimal_community_record, headers, es_clear
):

    """Test the validity of community shema"""
    client = client_with_login

    #Creta a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record)        
    )
    assert res.status_code == 201
    _assert_single_item_response(res)
    _assert_optional_items_metadata(res)

    created_community = res.json
    id_ = created_community['id'] 

    metadata_ = created_community['metadata']
    access_ = created_community['access']

    # Assert required fields
    assert 'title' in metadata_
    assert 'type' in metadata_
    assert 'visibility' in access_
    
    # Assert enums
    assert metadata_['type'] in ['organization', 'event', 'topic', 'project',]
    assert access_['visibility'] in ['public', 'private', 'hidden']


def test_post_metadata_schema_validation(
    app, client_with_login, location, minimal_community_record, headers, 
    es_clear
):
    """Test the validity of community metadata shema"""
    client = client_with_login

    # Assert field size constraints id
    data = copy.deepcopy(minimal_community_record)
    data["id"] = "".join([str(i) for i in range(101)]),
  
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(data)        
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred." 
    
    # Assert field size constraints title
    data['id'] = 'comm_id'
    data['metadata']['title'] = "".join([str(i) for i in range(251)])
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(data)        
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."

    # Assert field size constraints description
    data['metadata']['title'] = 'Title'
    data['metadata']['description'] = "".join([str(i) for i in range(1001)])
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(data)        
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    
    # Create community
    data['metadata']['description'] = "New community"
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(data)        
    )
    assert res.status_code == 201
    _assert_single_item_response(res)


def test_create_community_with_existing_id(
    app, client_with_login, location, minimal_community_record, headers,
    es_clear
):
    """Test creation of two community with the same id"""
    client = client_with_login
    
    #Creta a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record)        
    )
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    #Creta another community with the same id
    minimal_community_record['id'] = id_  
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record)        
    )
    assert res.status_code == 400
    assert res.json['message'] == f'Community {id_} already exists'


def test_create_community_with_deleted_id(
    app, client_with_login, minimal_community_record, headers,
    es_clear
):
    """Test creation of a community with a deleted id"""
    client = client_with_login
    
    #Creta a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record))
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    # Delete community
    res = client.delete(f'/communities/{id_}', headers=headers)
    assert res.status_code == 204

    #Creta another community with the same id
    minimal_community_record['id'] = id_  
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record))
    assert res.status_code == 400
    assert res.json['message'] == f'Community {id_} already exists'
    

def test_self_link(
    app, client_with_login, minimal_community_record, headers,
    es_clear
): 
    """Test self links generated"""
    client = client_with_login
    
    #Creta a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record))
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    assert '/'.join(created_community['links']['self'].split('/')[-2:]) == f'communities/{id_}'
    

@pytest.mark.skip()
def test_get_response(app, client_with_login, minimal_community_record, headers,
    es_clear
):
    pass