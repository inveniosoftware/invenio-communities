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


def test_simple_flow(
        db, es_clear, community, client,
        community_owner, users):
    """Test basics operations on records."""
    # TODO
    # /api/communities/<comid>/requests/records/
    comid, community = community
    new_member = users[0]
    login_user_via_session(client, user=new_member)
    community_members_list_url = url_for(
        'invenio_communities_members.community_members_api',
        pid_value=comid.pid_value)

    resp = client.post(community_members_list_url)
    assert resp.status_code == 201
    community_member_id = resp.json['id']

    login_user_via_session(client, user=community_owner)
    community_member_url = url_for(
        'invenio_communities_members.community_requests_api',
        pid_value=comid.pid_value,
        membership_id=community_member_id)

    resp = client.get(community_member_url)
    assert resp.status_code == 200
    membership_links = resp.json['links']

    resp = client.post(membership_links['comment'],  json={
        'message': 'Hello there'
    })
    assert resp.status_code == 200

    login_user_via_session(client, user=new_member)
    resp = client.post(membership_links['comment'],  json={
        'message': 'Oh hi Mark'
    })
    assert resp.status_code == 200

    login_user_via_session(client, user=community_owner)
    resp = client.post(membership_links['accept'], json={
        'message': 'Welcome aboard. Im removing you soon', 'role': 'curator'
    })
    assert resp.status_code == 200
    assert resp.json['role'] == 'curator'

    resp = client.put(community_member_url,  json={
        'role': 'admin'
    })
    assert resp.status_code == 200
    assert resp.json['role'] == 'admin'

    resp = client.post(membership_links['comment'],  json={
        'message': 'Goodbye'
    })
    assert resp.status_code == 200

    resp = client.delete(community_member_url)
    assert resp == 204
