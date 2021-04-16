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
        'created', 'id', 'links', 'metadata', 'updated', 'access'
    ]

    for field in fields_to_check:
        assert field in response_fields


def _assert_optional_items_metadata(response):
    """Assert the fields present on the metadata """
    metadata_fields = response.json['metadata'].keys()
    fields_to_check = [
        "title", "description", "type", "website", "alternate_identifiers", "funding",
        "curation_policy", "page"
    ] # domains, affiliations removed
    for field in fields_to_check:
        assert field in metadata_fields


def _assert_single_item_search(response):
    """Assert the fields present on the metadata """
    response_fields = response.json.keys()
    fields_to_check = [
        "aggregations", "hits", "links", "sortBy"
    ]

    for field in fields_to_check:
        assert field in response_fields


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

    # Assert field size constraints 
    data = copy.deepcopy(minimal_community_record)
    data["id"] = "".join([str(i) for i in range(101)]),
    data['metadata']['title'] = "".join([str(i) for i in range(251)])
    data['metadata']['description'] = "".join([str(i) for i in range(1001)])
    
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(data)        
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred." 
    assert res.json["errors"][0]['field'] == 'id' 
    assert res.json["errors"][0]['messages'] == ['Not a valid string.']
    assert res.json["errors"][1]['field'] == 'title' 
    assert res.json["errors"][1]['messages'] == ['Title is too long.']
    assert res.json["errors"][2]['field'] == 'description' 
    assert res.json["errors"][2]['messages'] == ['Description is too long.']
    
    # Assert field size constraints 
    data['id'] = 'comm_id'
    data['metadata']['title'] = 'title'
    data['metadata']['description'] = "new community"

    # Create community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(data)        
    )
    assert res.status_code == 201
    _assert_single_item_response(res)
    

def test_post_community_with_existing_id(
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


def test_post_community_with_deleted_id(
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
    assert res.status_code == 201
    

def test_self_links(
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
    # assert '/'.join(created_community['links']['self'].split('/')[-2:]) == f'communities/{id_}'
    assert created_community['links']['self'] == f'https://127.0.0.1:5000/api/communities/{id_}'
    assert created_community['links']['self_html'] == f'https://127.0.0.1:5000/ui/communities/{id_}'


def test_simple_search_response(
    app, client_with_login, minimal_community_record, headers,
    es_clear
):
    """Test get/list and search functionality"""
    client = client_with_login
    # Create a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record))
    assert res.status_code == 201

    created_community = res.json
    id_ = created_community["id"]

    # Search for any commmunity
    res = client.get(
        f'/communities', query_string={'q': f''}, headers=headers)
    assert res.status_code == 200
    _assert_single_item_search(res)

    #import ipdb; ipdb.set_trace()
    assert res.json['hits']['total'] == 1
    assert res.json['hits']['hits'][0]['metadata'] == \
         created_community['metadata']
    
    # Create another community
    data = copy.deepcopy(minimal_community_record)
    data['id'] = "comm_id2"
    data['metadata']['title'] = 'new title'
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(data))
    assert res.status_code == 201
    
    id2_ = res.json["id"]

    # Search filter for the second commmunity
    res = client.get(
        f'/communities', query_string={'q':'new'}, headers=headers)
    assert res.status_code == 200
    _assert_single_item_search(res)
    assert res.json['hits']['total'] == 1
    assert res.json['hits']['hits'][0]['id'] == id2_

    # Sort by the oldest record, default is newest
    # TODO: What other keywords does 'sort' support?
    res = client.get(
    f'/communities', query_string={'q':'', 'sort':'oldest'}, headers=headers)
    assert res.status_code == 200
    assert res.json['hits']['hits'][0]['id'] == id_
    
    # Test for page and size
    res = client.get(
    f'/communities', query_string={'q':'', 'size':'5', 'page':'2'}, headers=headers)
    assert res.status_code == 200
    assert res.json['hits']['total'] == 2


def test_simple_get_response(
    app, client_with_login, headers, es_clear
):
    """Test get response"""
    client = client_with_login

    big_community_record = \
    {
    "access": {
        "visibility": "public",
        "member_policy": "open",
        "record_policy": "open",
    },
    "id": "my_community_id",
    "metadata": {
        "title": "My Community",
        "description": "This is an example Community.",
        "type": "event",
        "alternate_identifiers": [{"scheme": "ror", "identifier": "03yrm5c26"}],
        "curation_policy": "This is the kind of records we accept.",
        "page": "Information for my community.",
        "website": "https://inveniosoftware.org/", 
        "funding": ["OpenAIRE"],   
    }
    }

    # Create a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(big_community_record))
        
    assert res.status_code == 201
    id_ = res.json["id"]

    # Read the community
    res = client.get(f'/communities/{id_}', headers=headers)
    assert res.status_code == 200
    _assert_single_item_response(res)
    _assert_optional_items_metadata(res)

    # Read a non-existed community
    res = client.get(f'/communities/{id_[:-1]}', headers=headers)
    assert res.status_code == 404
    assert res.message == 'The persistent identifier does not exist.'


def test_simple_put_response(
    app, client_with_login, minimal_community_record, headers,
    es_clear
):
    """Test put response"""
    client = client_with_login
    # Create a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record))
    assert res.status_code == 201
    created_community = res.json
    id_ = created_community['id']

    data = copy.deepcopy(created_community)
    data["metadata"] = \
    {
        "title": "New Community",
        "description": "This is an example Community.",
        "type": "event",
        "alternate_identifiers": [{"scheme": "ror", "identifier": "03yrm5c26"}],
        "curation_policy": "This is the kind of records we accept.",
        "page": "Information for my community.",
        "website": "https://inveniosoftware.org/", 
        "funding": ["OpenAIRE"],   
    }
    
    res = client.put(
        f'/communities/{id_}', headers=headers, data=json.dumps(data))
    assert res.status_code == 200
    assert res.json['id'] == id_
    assert res.json['metadata'] == data["metadata"]
    assert res.json["revision_id"] == int(data["revision_id"])+1

    # Update non-existing community
    res = client.put(
        f'/communities/{id_[:-1]}', headers=headers, data=json.dumps(data))
    assert res.status_code == 404
    assert res.json['message'] == 'The persistent identifier does not exist.'



def test_simple_delete_response(
    app, client_with_login, minimal_community_record, headers,
    es_clear
):
    """Test delete and request deleted community """
    client = client_with_login
    
    #Creta a community
    res = client.post(
        '/communities', headers=headers,
        data=json.dumps(minimal_community_record))
    assert res.status_code == 201
    #_assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    # Delete community
    res = client.delete(f'/communities/{id_}', headers=headers)
    assert res.status_code == 204

    # Read the community
    res = client.get(f'/communities/{id_}', headers=headers)
    assert res.status_code == 410
    assert res.json['message']  == 'The record has been deleted.'

    # Delete non-existing community
    res = client.delete(f'/communities/{id_[:-1]}', headers=headers)
    assert res.status_code == 404
    assert res.json['message']  == 'The persistent identifier does not exist.'