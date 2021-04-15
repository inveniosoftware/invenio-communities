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
def test_simple_flow(db, es_clear, community, accepted_community_record, client, community_owner):
    """Test basic operations on collections."""
    comid, community = community

    collections_list_url = url_for(
        'invenio_communities_collections.collections_list',
        pid_value=comid.pid_value)

    # list
    resp = client.get(collections_list_url)
    assert resp.status_code == 200
    assert resp.json == {}

    # create
    collection_data = {
        'id': 'test',
        'title': 'Test collection',
        'description': 'Test collection description',
    }

    resp = client.post(collections_list_url, json=collection_data)
    assert resp.status_code == 401

    login_user_via_session(client, user=community_owner)
    resp = client.post(collections_list_url, json=collection_data)
    assert resp.status_code == 201
    created_resp_json = resp.json
    collection_item_url = created_resp_json['links']['self']
    assert created_resp_json == {
        'title': collection_data['title'],
        'description': collection_data['description'],
        'links': {
            'self': '/communities/{}/collections/test'.format(comid.pid_value)
        },
    }

    # read
    resp = client.get(collection_item_url)
    assert resp.status_code == 200
    assert resp.json == created_resp_json

    # update
    resp = client.put(collection_item_url, json={
        'title': 'New test title',
        # NOTE: removes description
    })
    assert resp.status_code == 200
    assert resp.json == {
        'title': 'New test title',
        'description': None,
        'links': {'self': collection_item_url},
    }

    # get record collections
    community_record_url = url_for(
        'invenio_communities_collections.records',
        pid_value=comid.pid_value,
        record_pid=accepted_community_record.record.pid.pid_value
    )
    resp = client.get(community_record_url)
    assert resp.status_code == 200
    assert '_collections' not in resp.json

    # update record collections
    resp = client.put(community_record_url, json={
        'collections': [{'id': 'test'}]
    })
    assert resp.status_code == 200
    assert resp.json['_collections'] == [{'id': 'test'}]

    # delete
    resp = client.delete(collection_item_url)
    assert resp.status_code == 204
    resp = client.get(collection_item_url)
    assert resp.status_code == 404


@pytest.mark.skip()
def test_permissions(db, es_clear, community, accepted_community_record, client, community_owner, authenticated_user, record_owner):
    """Test collection permissions."""
    # TODO: write tests for permissions
    pass
