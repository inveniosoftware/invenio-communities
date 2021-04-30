# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community resources tests."""

import copy
from io import BytesIO

from invenio_communities.communities.records.api import Community


def _assert_single_item_response(response):
    """Assert the fields present on a single item response."""
    response_fields = response.json.keys()
    fields_to_check = [
        'created', 'id', 'links', 'metadata', 'updated'
    ]

    for field in fields_to_check:
        assert field in response_fields


def _assert_optional_medatada_items_response(response):
    """Assert the fields present on the metadata"""
    metadata_fields = response.json['metadata'].keys()
    fields_to_check = [
        "description", "curation_policy", "page", "website",
        "funding", "organizations"
    ]

    for field in fields_to_check:
        assert field in metadata_fields


def _assert_optional_access_items_response(response):
    """Assert the fields present on the metadata"""
    access_fields = response.json['access'].keys()
    fields_to_check = [
       "visibility", "member_policy", "record_policy", "owned_by",
    ]

    for field in fields_to_check:
        assert field in access_fields


def _assert_single_item_search(response):
    """Assert the fields present on the search response """
    response_fields = response.json.keys()
    fields_to_check = [
        "aggregations", "hits", "links", "sortBy"
    ]

    for field in fields_to_check:
        assert field in response_fields


def _assert_error_fields_response(expected, response):
    """Assert the fields present in response error list and fields tested """
    error_fields = [item['field'] for item in response.json['errors']]

    for field in expected:
        assert field in error_fields


def _assert_error_messages_response(expected, response):
    """Assert the error messages present in response error list and expected error messages """
    error_messages_list = ['Must be one of: organization, event, topic, project.',
                           'Must be one of: public, private.',
                           'Must be one of: public, restricted.',
                           'Not empty string and less than 2000 characters allowed.',
                           'Not empty string and less than 250 characters allowed.',
                           'Not empty string and less than 100 characters allowed.'
                          ]
    error_messages = set([item['messages'][0] for item in response.json['errors']])

    assert expected == len(set(error_messages_list).intersection(error_messages))


def test_simple_flow(
    app, client_with_login, location, minimal_community, headers,
    es_clear
):
    """Test a simple REST API flow."""
    client = client_with_login
    # Create a community
    res = client.post(
        '/communities', headers=headers,
        json=minimal_community)
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
        f'/communities/{id_}', headers=headers, json=data)
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

    # Read again community, should return 404
    res = client.get(f'/communities/{id_}', headers=headers)
    assert res.status_code == 410
    assert res.json["message"] == "The record has been deleted."


def test_post_schema_validation(
    app, client_with_login, location, minimal_community, headers,
    es_clear
):
    """Test the validity of community json schema"""
    client = client_with_login

    # Create a community
    res = client.post('/communities', headers=headers, json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    assert minimal_community['metadata'] == created_community['metadata']

    # Assert required fields
    assert created_community['metadata'] == {"title": "Title", "type": "topic"}
    assert created_community['access']['visibility'] == "public"

    # Assert required enums
    data = copy.deepcopy(minimal_community)
    data['metadata']['type'] = 'foobar'
    res = client.post('/communities', headers=headers, json=data)
    assert res.status_code == 400

    data = copy.deepcopy(minimal_community)
    data['access']['visibility'] = 'foobar'
    res = client.post('/communities', headers=headers, json=data)
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    _assert_error_fields_response(set(['access.visibility']), res)
    _assert_error_messages_response(1, res)

    # Delete the community
    res = client.delete(f'/communities/{created_community["id"]}', headers=headers)
    assert res.status_code == 204


def test_post_metadata_schema_validation(
    app, client_with_login, location, minimal_community, headers
):
    """Test the validity of community metadata schema"""
    client = client_with_login

    # Alter paypload for each field for test
    data = copy.deepcopy(minimal_community)

    # Assert field size constraints  (id, title, description, curation policy, page)
    # ID max 100
    data["id"] = "x" * 101
    res = client.post(
        '/communities', headers=headers, json=data
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]['field'] == 'id'
    #assert res.json["errors"][0]['messages'] == ['Not a valid string.']

    # Title max 250
    data["id"] = "my_comm"
    data['metadata']['title'] =  "x" * 251
    res = client.post(
        '/communities', headers=headers, json=data
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]['field'] == 'metadata.title'
    #assert res.json["errors"][0]['messages'] == ['Title is too long.']

    # Description max 2000
    data['metadata']['title'] = "New Title"
    data['metadata']['description'] =  "x" * 2001
    res = client.post(
        '/communities', headers=headers, json=data
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]['field'] == 'metadata.description'
    #assert res.json["errors"][0]['messages'] == ['Description is too long.']

    # Curation policy max 2000
    data['metadata']['description'] = "basic description"
    data['metadata']['curation_policy'] =  "x" * 2001
    res = client.post(
        '/communities', headers=headers, json=data
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]['field'] == 'metadata.curation_policy'
    #assert res.json["errors"][0]['messages'] == ['Curation policy is too long.']

    # Curation policy max 2000
    data['metadata']['curation_policy'] = "no policy"
    data['metadata']['page'] = "".join([str(i) for i in range(2001)])
    res = client.post(
        '/communities', headers=headers, json=data
    )
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]['field'] == 'metadata.page'
    #assert res.json["errors"][0]['messages'] == ['Page is too long.']

    data['metadata']['page'] = "basic page"
    res = client.post(
        '/communities', headers=headers, json=data
    )
    assert res.status_code == 201
    _assert_single_item_response(res)

    # Delete the community
    res = client.delete(f'/communities/{data["id"]}', headers=headers)
    assert res.status_code == 204


def test_post_community_with_existing_id(
    app, client_with_login, location, minimal_community, headers
):
    """Test create two communities with the same id"""
    client = client_with_login

    #Creta a community
    res = client.post(
        '/communities', headers=headers,
        json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    #Creta another community with the same id
    minimal_community['id'] = id_
    res = client.post(
        '/communities', headers=headers,
        json=minimal_community)
    assert res.status_code == 400
    assert res.json['errors'][0]['messages'][0] == \
        'A community with this identifier already exists.'

    # Delete the community
    res = client.delete(f'/communities/{id_}', headers=headers)
    assert res.status_code == 204


def test_post_community_with_deleted_id(
    app, client_with_login, location, minimal_community, headers
):
    """Test create a community with a deleted id"""
    client = client_with_login

    #Creta a community
    res = client.post(
        '/communities', headers=headers,
        json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    # Delete community
    res = client.delete(f'/communities/{id_}', headers=headers)
    assert res.status_code == 204

    #Creta another community with the same id
    minimal_community['id'] = id_
    res = client.post(
        '/communities', headers=headers,
        json=minimal_community)
    assert res.status_code == 400
    assert res.json['errors'][0]['messages'][0] == \
        'A community with this identifier already exists.'


def test_post_self_links(
    app, client_with_login, location, minimal_community, headers
):
    """Test self links generated after post"""
    client = client_with_login

    #Creta a community
    res = client.post(
        '/communities', headers=headers,
        json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']
    # assert '/'.join(created_community['links']['self'].split('/')[-2:]) == f'communities/{id_}'
    assert created_community['links']['self'] == f'https://127.0.0.1:5000/api/communities/{id_}'
    assert created_community['links']['self_html'] == f'https://127.0.0.1:5000/communities/{id_}'

    # Delete the community
    res = client.delete(f'/communities/{id_}', headers=headers)
    assert res.status_code == 204


def test_simple_search_response(
    app, client_with_login, location, minimal_community, create_many_records, headers,
    es_clear
):
    """Test get/list and search functionality"""
    client = client_with_login

    # Create many communities,
    id_oldest, id_newest, num_each, total = create_many_records

    # Search for any commmunity, default order newest
    res = client.get(
        f'/communities', query_string={'q': f''}, headers=headers)
    assert res.status_code == 200
    _assert_single_item_search(res)
    assert res.json['hits']['total'] == total
    assert res.json['hits']['hits'][0]['id'] == id_newest
    assert res.json['hits']['hits'][0]['metadata'] == minimal_community['metadata']

    # Search filter for the second commmunity
    res = client.get(
        f'/communities', query_string={'type':'project'}, headers=headers)
    assert res.status_code == 200
    _assert_single_item_search(res)
    assert res.json['hits']['total'] == num_each

    # Sort results by oldest
    res = client.get(
    f'/communities', query_string={'q':'', 'sort':'oldest'}, headers=headers)
    assert res.status_code == 200
    assert res.json['hits']['hits'][0]['id'] == id_oldest

    # Test for page and size
    res = client.get(
    f'/communities', query_string={'q':'', 'size':'5', 'page':'2'}, headers=headers)
    assert res.status_code == 200
    assert res.json['hits']['total'] == total
    assert len(res.json['hits']['hits']) == 5


def test_simple_get_response(
    app, client_with_login, location, full_community, headers
):
    """Test get response json schema"""
    client = client_with_login
    # Create a community
    res = client.post(
        '/communities', headers=headers, json=full_community
    )
    assert res.status_code == 201
    _assert_single_item_response(res)
    _assert_optional_medatada_items_response(res)

    created_community = res.json

    # assert full_community['access'] == created_community['access']
    assert full_community['metadata'] == created_community['metadata']
    id_ = created_community["id"]

    # Read the community
    res = client.get(f'/communities/{id_}', headers=headers)
    assert res.status_code == 200
    _assert_single_item_response(res)
    _assert_optional_medatada_items_response(res)
    # _assert_optional_access_items_response(res)
    # assert full_community['access'] == res.json['access']
    assert full_community['metadata'] == res.json['metadata']

    # Read a non-existed community
    res = client.get(f'/communities/{id_[:-1]}', headers=headers)
    assert res.status_code == 404
    # assert res.message == 'The persistent identifier does not exist.'


def test_simple_put_response(
    app, client_with_login, location, minimal_community, headers,
    es_clear
):
    """Test put response basic functionality"""
    client = client_with_login
    # Create a community
    res = client.post(
        '/communities', headers=headers,
        json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    data = copy.deepcopy(minimal_community)
    data["metadata"] = \
    {
        "title": "New Community",
        "description": "This is an example Community.",
        "type": "event",
        "curation_policy": "This is the kind of records we accept.",
        "page": "Information for my community.",
        "website": "https://inveniosoftware.org/",
    }

    data["access"] = \
    {
        "visibility": "restricted",
        "member_policy": "closed",
        "record_policy": "restricted"
    }

    res = client.put(f'/communities/{id_}', headers=headers, json=data)
    assert res.status_code == 200
    assert res.json['id'] == id_
    assert res.json['metadata'] == data["metadata"]
    # assert access_== data["access"]
    assert res.json["revision_id"] == int(created_community["revision_id"])+1

    # Update non-existing community
    res = client.put(
        f'/communities/{id_[:-1]}', headers=headers, json=data
    )
    assert res.status_code == 404
    assert res.json['message'] == 'The persistent identifier does not exist.'

    # Update deleted community
    res = client.delete(f'/communities/{id_}', headers=headers)
    assert res.status_code == 204
    data['metadata']['title'] =  "Deleted Community",
    res = client.put(f'/communities/{id_}', headers=headers, json=data)
    assert res.status_code == 410
    assert res.json['message']  == 'The record has been deleted.'


def test_update_renamed_record(
    app, client_with_login, location, minimal_community, headers,
    es_clear
):
    """Test to update renamed entity."""
    client = client_with_login
    # Create a community
    res = client.post('/communities', headers=headers, json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    # Rename the communnity
    data = copy.deepcopy(minimal_community)
    data['id'] = "renamed_comm"
    res = client.post(f'/communities/{id_}/rename', headers=headers, json=data)
    assert res.status_code == 200
    renamed_community = res.json
    renamed_id_ = renamed_community['id']
    data["access"] = \
        {
            "visibility": "restricted",
            "member_policy": "closed",
            "record_policy": "restricted"
        }
    res = client.put(f'/communities/{renamed_id_}', headers=headers, json=data)
    assert res.status_code == 200
    assert res.json['id'] == renamed_id_
    assert res.json['metadata'] == data["metadata"]
    # assert access_== data["access"]
    assert res.json["revision_id"] == int(renamed_community["revision_id"])+1


def test_simple_delete_response(
    app, client_with_login, location, minimal_community, headers,
    es_clear
):
    """Test delete and request deleted community."""
    client = client_with_login

    # Create a community
    res = client.post(
        '/communities', headers=headers,
        json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
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


def test_logo_flow(
    app, client_with_login, location, minimal_community, headers, es_clear
):
    """Test logo workflow."""
    client = client_with_login

    # Create a community
    res = client.post('/communities', headers=headers, json=minimal_community)
    assert res.status_code == 201
    created_community = res.json
    id_ = created_community['id']
    assert created_community['links']['logo'] == \
        f'https://127.0.0.1:5000/api/communities/{id_}/logo'

    # Get non-existent logo
    res = client.get(f'/communities/{id_}/logo')
    assert res.status_code == 404
    assert res.json['message'] == 'No logo exists for this community.'

    # Delete non-existent logo
    res = client.delete(f'/communities/{id_}/logo', headers=headers)
    assert res.status_code == 404
    assert res.json['message'] == 'No logo exists for this community.'

    # Update logo
    res = client.put(
        f'/communities/{id_}/logo',
        headers={
            **headers,
            'content-type': 'application/octet-stream',
        },
        data=BytesIO(b'logo'),
    )
    assert res.status_code == 200
    assert res.json['size'] == 4

    # Get logo
    res = client.get(f'/communities/{id_}/logo')
    assert res.status_code == 200
    assert res.data == b'logo'

    # Update logo again
    res = client.put(
        f'/communities/{id_}/logo',
        headers={
            **headers,
            'content-type': 'application/octet-stream',
        },
        data=BytesIO(b'new_logo'),
    )
    assert res.status_code == 200
    assert res.json['size'] == 8

    # Get new logo
    res = client.get(f'/communities/{id_}/logo')
    assert res.status_code == 200
    assert res.data == b'new_logo'

    # Delete logo
    res = client.delete(f'/communities/{id_}/logo', headers=headers)
    assert res.status_code == 204

    # Try to get deleted logo
    res = client.get(f'/communities/{id_}/logo')
    assert res.status_code == 404
    assert res.json['message'] == 'No logo exists for this community.'

    # TODO: Delete community and try all of the above operations
    # TODO: Check permissions


def test_invalid_community_ids(
    app, client_with_login, location, minimal_community, headers,
    es_clear
):
    """Test for invalid community IDs handling."""
    client = client_with_login
    # Create a community with invalid ID
    minimal_community['id'] = 'comm id'
    res = client.post('/communities', headers=headers, json=minimal_community)
    assert res.status_code == 400
    assert res.json['errors'][0]['messages'][0] == \
        'The ID should contain only letters with numbers or dashes.'

    minimal_community['id'] = 'comm_id'
    res = client.post('/communities', headers=headers, json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community['id']

    # Rename the communnity
    data = copy.deepcopy(minimal_community)
    data['id'] = "Renamed comm"
    res = client.post(f'/communities/{id_}/rename', headers=headers, json=data)
    assert res.status_code == 400
    assert res.json['errors'][0]['messages'][0] == \
        'The ID should contain only letters with numbers or dashes.'

    data = copy.deepcopy(minimal_community)
    data = {}
    res = client.post(f'/communities/{id_}/rename', headers=headers, json=data)
    assert res.status_code == 400
    assert res.json['errors'][0]['messages'][0] == \
        'Missing data for required field.'

    new_id = "Renamed_comm"
    data['id'] = new_id
    res = client.post(f'/communities/{id_}/rename', headers=headers, json=data)
    assert res.status_code == 200
    assert res.json['id'] == new_id.lower()
