# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2022 Northwestern University.
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community resources tests."""

import copy
from io import BytesIO
from uuid import uuid4

from invenio_communities.communities.records.api import Community
from invenio_communities.members import Member


def _assert_single_item_response(response):
    """Assert the fields present on a single item response."""
    response_fields = response.json.keys()
    fields_to_check = [
        "created",
        "id",
        "links",
        "metadata",
        "slug",
        "updated",
    ]

    for field in fields_to_check:
        assert field in response_fields


def _assert_optional_medatada_items_response(response):
    """Assert the fields present on the metadata"""
    metadata_fields = response.json["metadata"].keys()
    fields_to_check = [
        "description",
        "curation_policy",
        "page",
        "website",
        "organizations",
    ]

    for field in fields_to_check:
        assert field in metadata_fields


def _assert_optional_access_items_response(response):
    """Assert the fields present on the metadata"""
    access_fields = response.json["access"].keys()
    fields_to_check = [
        "visibility",
        "member_policy",
        "record_policy",
    ]

    for field in fields_to_check:
        assert field in access_fields


def _assert_single_item_search(response):
    """Assert the fields present on the search response"""
    response_fields = response.json.keys()
    fields_to_check = ["aggregations", "hits", "links", "sortBy"]

    for field in fields_to_check:
        assert field in response_fields


def _assert_error_fields_response(expected, response):
    """Assert the fields present in response error list and fields tested"""
    error_fields = [item["field"] for item in response.json["errors"]]

    for field in expected:
        assert field in error_fields


def _assert_error_messages_response(expected, response):
    """Assert the error messages present in response error list and expected error messages"""
    error_messages_list = [
        "Must be one of: organization, event, topic, project.",
        "Must be one of: public, private.",
        "Must be one of: public, restricted.",
        "Not empty string and less than 2000 characters allowed.",
        "Not empty string and less than 250 characters allowed.",
        "Not empty string and less than 100 characters allowed.",
    ]
    error_messages = set([item["messages"][0] for item in response.json["errors"]])

    assert expected == len(set(error_messages_list).intersection(error_messages))


def test_simple_flow(
    client, location, minimal_community, headers, owner, db, search_clear
):
    """Test a simple REST API flow."""
    client = owner.login(client)

    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)

    created_community = res.json
    id_ = created_community["id"]
    slug = created_community["slug"]

    # Read the community
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["metadata"] == created_community["metadata"]

    read_community = res.json
    Community.index.refresh()

    # Read the community via slug
    res = client.get(f"/communities/{slug}", headers=headers)
    assert res.status_code == 200
    assert res.json["id"] == id_

    # Search for created community
    res = client.get(f"/communities", query_string={"q": f"id:{id_}"}, headers=headers)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["metadata"] == created_community["metadata"]

    # Update community
    data = copy.deepcopy(read_community)
    data["metadata"]["title"] = "New title"
    res = client.put(f"/communities/{id_}", headers=headers, json=data)
    assert res.status_code == 200
    assert res.json["metadata"]["title"] == "New title"

    updated_community = res.json
    Community.index.refresh()

    # Search for updated commmunity
    res = client.get(f"/communities", query_string={"q": f"id:{id_}"}, headers=headers)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["metadata"] == updated_community["metadata"]
    data = res.json["hits"]["hits"][0]
    assert updated_community["metadata"]["title"] == "New title"

    # Delete community
    res = client.delete(f"/communities/{id_}", headers=headers)
    assert res.status_code == 204

    # Read again community, should return 404
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.status_code == 410
    assert res.json["message"] == "The record has been deleted."


def test_post_schema_validation(
    client, location, minimal_community, headers, owner, search_clear, db
):
    """Test the validity of community json schema"""
    client = owner.login(client)

    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    assert minimal_community["metadata"] == created_community["metadata"]

    # Assert required fields
    assert created_community["metadata"] == {"title": "My Community"}
    assert created_community["access"]["visibility"] == "public"

    # Assert required enums
    data = copy.deepcopy(minimal_community)
    data["metadata"]["type"] = {"id": "foobar", "title": "foobar"}
    res = client.post("/communities", headers=headers, json=data)
    assert res.status_code == 400

    data = copy.deepcopy(minimal_community)
    data["access"]["visibility"] = "foobar"
    res = client.post("/communities", headers=headers, json=data)
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    _assert_error_fields_response(set(["access.visibility"]), res)
    _assert_error_messages_response(1, res)

    # Delete the community
    res = client.delete(f'/communities/{created_community["id"]}', headers=headers)
    assert res.status_code == 204


def test_post_metadata_schema_validation(
    client, location, minimal_community, headers, db, owner, search_clear
):
    """Test the validity of community metadata schema"""
    client = owner.login(client)

    # Alter paypload for each field for test
    data = copy.deepcopy(minimal_community)

    # Assert field size constraints  (id, title, description, curation policy, page)
    # ID max 100
    data["slug"] = "x" * 101
    res = client.post("/communities", headers=headers, json=data)
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]["field"] == "slug"
    # assert res.json["errors"][0]['messages'] == ['Not a valid string.']

    # Title max 250
    data["slug"] = "my_comm"
    data["metadata"]["title"] = "x" * 251
    res = client.post("/communities", headers=headers, json=data)
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]["field"] == "metadata.title"
    # assert res.json["errors"][0]['messages'] == ['Title is too long.']

    # Description max 250
    data["metadata"]["title"] = "New Title"
    data["metadata"]["description"] = "x" * 251
    res = client.post("/communities", headers=headers, json=data)
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]["field"] == "metadata.description"
    # assert res.json["errors"][0]['messages'] == ['Description is too long.']

    # Curation policy max 50000
    data["metadata"]["description"] = "basic description"
    data["metadata"]["curation_policy"] = "x" * 50001
    res = client.post("/communities", headers=headers, json=data)
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]["field"] == "metadata.curation_policy"
    # assert res.json["errors"][0]['messages'] == ['Curation policy is too long.']

    # Curation policy max 50000
    data["metadata"]["curation_policy"] = "no policy"
    data["metadata"]["page"] = "".join([str(i) for i in range(50001)])
    res = client.post("/communities", headers=headers, json=data)
    assert res.status_code == 400
    assert res.json["message"] == "A validation error occurred."
    assert res.json["errors"][0]["field"] == "metadata.page"
    # assert res.json["errors"][0]['messages'] == ['Page is too long.']

    data["metadata"]["page"] = "basic page"
    res = client.post("/communities", headers=headers, json=data)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)

    # Delete the community
    res = client.delete(f'/communities/{data["slug"]}', headers=headers)
    assert res.status_code == 204


def test_post_community_with_existing_id(
    client, location, minimal_community, headers, db, search_clear, owner
):
    """Test create two communities with the same id"""
    client = owner.login(client)

    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community["id"]

    # Creta another community with the same id
    minimal_community["id"] = id_
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 400
    assert (
        res.json["errors"][0]["messages"][0]
        == "A community with this identifier already exists."
    )

    # Delete the community
    res = client.delete(f"/communities/{id_}", headers=headers)
    assert res.status_code == 204


def test_post_community_with_deleted_id(
    client, location, minimal_community, headers, db, search_clear, owner
):
    """Test create a community with a deleted id"""
    client = owner.login(client)

    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community["id"]

    # Delete community
    res = client.delete(f"/communities/{id_}", headers=headers)
    assert res.status_code == 204

    # Create another community with the same id
    minimal_community["id"] = id_
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 400
    assert (
        res.json["errors"][0]["messages"][0]
        == "A community with this identifier already exists."
    )


def test_post_self_links(
    client, location, minimal_community, headers, db, search_clear, owner
):
    """Test self links generated after post"""
    client = owner.login(client)

    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community["id"]
    slug = created_community["slug"]
    # assert '/'.join(created_community['links']['self'].split('/')[-2:]) == f'communities/{id_}'
    assert (
        created_community["links"]["self"]
        == f"https://127.0.0.1:5000/api/communities/{id_}"
    )
    assert (
        created_community["links"]["self_html"]
        == f"https://127.0.0.1:5000/communities/{slug}"
    )

    # Delete the community
    res = client.delete(f"/communities/{id_}", headers=headers)
    assert res.status_code == 204


def test_simple_search_response(
    client,
    location,
    minimal_community,
    owner,
    headers,
    search_clear,
    fake_communities,
    community_types,
):
    """Test get/list and search functionality"""
    client = owner.login(client)

    community_copy = copy.deepcopy(minimal_community)
    community_copy["metadata"]["type"] = community_types[-1]

    # Create many communities,
    slug_oldest, slug_newest, num_each, total = fake_communities

    # Search for any commmunity, default order newest
    res = client.get(f"/communities", query_string={"q": f""}, headers=headers)
    assert res.status_code == 200
    _assert_single_item_search(res)
    assert res.json["hits"]["total"] == total
    assert res.json["hits"]["hits"][0]["slug"] == slug_newest
    assert res.json["hits"]["hits"][0]["metadata"] == community_copy["metadata"]

    # Search filter for the second commmunity
    res = client.get(
        f"/communities", query_string={"q": "metadata.type.id:project"}, headers=headers
    )
    assert res.status_code == 200
    _assert_single_item_search(res)
    assert res.json["hits"]["total"] == num_each

    # Sort results by oldest
    res = client.get(
        f"/communities", query_string={"q": "", "sort": "oldest"}, headers=headers
    )
    assert res.status_code == 200
    assert res.json["hits"]["hits"][0]["slug"] == slug_oldest

    # Test for page and size
    res = client.get(
        f"/communities",
        query_string={"q": "", "size": "5", "page": "2"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == total
    assert len(res.json["hits"]["hits"]) == 5


def test_simple_get_response(
    client,
    location,
    full_community,
    headers,
    db,
    search_clear,
    owner,
    community_type_record,
):
    """Test get response json schema"""
    client = owner.login(client)
    community_copy = copy.deepcopy(full_community)
    # Dereferenced community has attribute 'title' in 'type'
    community_copy["metadata"]["type"].update({"title": {"en": "Event"}})

    # Create a community
    res = client.post("/communities", headers=headers, json=full_community)
    Member.index.refresh()
    assert res.status_code == 201
    _assert_single_item_response(res)
    _assert_optional_medatada_items_response(res)

    created_community = res.json

    # assert full_community['access'] == created_community['access']

    assert community_copy["metadata"] == created_community["metadata"]
    id_ = created_community["id"]

    # Read the community
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.status_code == 200
    _assert_single_item_response(res)
    _assert_optional_medatada_items_response(res)
    # _assert_optional_access_items_response(res)
    # assert full_community['access'] == res.json['access']
    assert community_copy["metadata"] == res.json["metadata"]

    # Read a non-existed community
    res = client.get(f"/communities/{id_[:-1]}", headers=headers)
    assert res.status_code == 404
    # assert res.message == 'The persistent identifier does not exist.'


def test_simple_put_response(
    client,
    location,
    minimal_community,
    headers,
    db,
    search_clear,
    owner,
    community_type_record,
):
    """Test put response basic functionality"""
    client = owner.login(client)
    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community["id"]
    Member.index.refresh()

    data = copy.deepcopy(minimal_community)
    data["metadata"] = {
        "title": "New Community",
        "description": "This is an example Community.",
        "type": {
            "id": "event",
        },
        "curation_policy": "This is the kind of records we accept.",
        "page": "Information for my community.",
        "website": "https://inveniosoftware.org/",
    }

    data["access"] = {
        "visibility": "restricted",
        "members_visibility": "restricted",
        "member_policy": "closed",
        "record_policy": "closed",
    }

    res = client.put(f"/communities/{id_}", headers=headers, json=data)
    # Dereferenced community has attribute 'title' in 'type'
    data["metadata"]["type"].update({"title": {"en": "Event"}})
    assert res.status_code == 200
    assert res.json["id"] == id_
    assert res.json["metadata"] == data["metadata"]
    # assert access_== data["access"]
    assert res.json["revision_id"] == int(created_community["revision_id"]) + 1

    # Update non-existing community
    res = client.put(f"/communities/{id_[:-1]}", headers=headers, json=data)
    assert res.status_code == 404
    assert res.json["message"] == "The persistent identifier does not exist."

    # Update deleted community
    res = client.delete(f"/communities/{id_}", headers=headers)
    assert res.status_code == 204
    data["metadata"]["title"] = "Deleted community"
    res = client.put(f"/communities/{id_}", headers=headers, json=data)
    assert res.status_code == 410
    assert res.json["message"] == "The record has been deleted."


def test_update_renamed_record(
    client, location, minimal_community, headers, db, search_clear, owner
):
    """Test to update renamed entity."""
    client = owner.login(client)
    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community["id"]
    slug = created_community["slug"]

    # Rename the community
    data = copy.deepcopy(minimal_community)
    data["slug"] = "renamed_comm"
    res = client.post(f"/communities/{id_}/rename", headers=headers, json=data)
    assert res.status_code == 200
    renamed_community = res.json
    renamed_id_ = renamed_community["id"]
    data["access"] = {
        "visibility": "restricted",
        "members_visibility": "restricted",
        "member_policy": "closed",
        "record_policy": "closed",
    }
    res = client.put(f"/communities/{renamed_id_}", headers=headers, json=data)
    assert res.status_code == 200
    assert res.json["id"] == renamed_id_
    assert res.json["metadata"] == data["metadata"]
    assert res.json["revision_id"] == int(renamed_community["revision_id"]) + 1


def test_simple_delete_response(
    client, location, minimal_community, headers, db, search_clear, owner
):
    """Test delete and request deleted community."""
    client = owner.login(client)

    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community["id"]

    # Delete community
    res = client.delete(f"/communities/{id_}", headers=headers)
    assert res.status_code == 204

    # Read the community
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.status_code == 410
    assert res.json["message"] == "The record has been deleted."

    # Delete non-existing community
    res = client.delete(f"/communities/{id_[:-1]}", headers=headers)
    assert res.status_code == 404
    assert res.json["message"] == "The persistent identifier does not exist."


def test_logo_flow(
    app, client, location, minimal_community, headers, db, search_clear, owner
):
    """Test logo workflow."""
    client = owner.login(client)

    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 201
    created_community = res.json
    id_ = created_community["id"]
    assert (
        created_community["links"]["logo"]
        == f"https://127.0.0.1:5000/api/communities/{id_}/logo"
    )
    Member.index.refresh()

    # Get non-existent logo
    res = client.get(f"/communities/{id_}/logo")
    assert res.status_code == 404
    assert res.json["message"] == "No logo exists for this community."

    # Delete non-existent logo
    res = client.delete(f"/communities/{id_}/logo", headers=headers)
    assert res.status_code == 404
    assert res.json["message"] == "No logo exists for this community."

    # Update logo
    res = client.put(
        f"/communities/{id_}/logo",
        headers={
            **headers,
            "content-type": "application/octet-stream",
        },
        data=BytesIO(b"logo"),
    )
    assert res.status_code == 200
    assert res.json["size"] == 4

    # Get logo
    res = client.get(f"/communities/{id_}/logo")
    assert res.status_code == 200
    assert res.data == b"logo"

    # Update logo again
    res = client.put(
        f"/communities/{id_}/logo",
        headers={
            **headers,
            "content-type": "application/octet-stream",
        },
        data=BytesIO(b"new_logo"),
    )
    assert res.status_code == 200
    assert res.json["size"] == 8

    # Get new logo
    res = client.get(f"/communities/{id_}/logo")
    assert res.status_code == 200
    assert res.data == b"new_logo"

    # Delete logo with unauthorized user
    with app.test_client() as anon_client:
        res = anon_client.delete(f"/communities/{id_}/logo", headers=headers)
        assert res.status_code == 403

    # Delete logo
    res = client.delete(f"/communities/{id_}/logo", headers=headers)
    assert res.status_code == 204

    # Try to get deleted logo
    res = client.get(f"/communities/{id_}/logo")
    assert res.status_code == 404
    assert res.json["message"] == "No logo exists for this community."

    # TODO: Delete community and try all of the above operations


def test_logo_max_content_length(
    app, client, location, minimal_community, headers, db, search_clear, owner
):
    """Test logo max size."""
    client = owner.login(client)

    # Create a community
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 201
    created_community = res.json
    id_ = created_community["id"]
    assert (
        created_community["links"]["logo"]
        == f"https://127.0.0.1:5000/api/communities/{id_}/logo"
    )
    Member.index.refresh()

    # Update app max size for community logos
    max_size = 10**6
    app.config["COMMUNITIES_LOGO_MAX_FILE_SIZE"] = max_size

    # Update logo with big content
    logo_data = b"logo" * (max_size + 1)
    res = client.put(
        f"/communities/{id_}/logo",
        headers={
            **headers,
            "content-type": "application/octet-stream",
        },
        data=BytesIO(logo_data),
    )
    assert res.status_code == 400

    # Update logo with small content
    logo_data = b"logo"
    res = client.put(
        f"/communities/{id_}/logo",
        headers={
            **headers,
            "content-type": "application/octet-stream",
        },
        data=BytesIO(logo_data),
    )
    assert res.status_code == 200


def test_invalid_community_ids_create(
    client, location, minimal_community, headers, db, search_clear, owner
):
    client = owner.login(client)
    # Create a community with invalid ID
    minimal_community["slug"] = "comm id"
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 400
    assert (
        res.json["errors"][0]["messages"][0]
        == "The ID should contain only letters with numbers or dashes."
    )


def test_invalid_community_ids(
    client, location, minimal_community, headers, db, search_clear, owner
):
    """Test for invalid community IDs handling."""
    client = owner.login(client)

    minimal_community["slug"] = "comm_id"
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community["id"]
    Member.index.refresh()

    # Rename the community
    data = copy.deepcopy(minimal_community)
    data["slug"] = "Renamed comm"
    res = client.post(f"/communities/{id_}/rename", headers=headers, json=data)
    assert res.status_code == 400
    assert (
        res.json["errors"][0]["messages"][0]
        == "The ID should contain only letters with numbers or dashes."
    )

    data = copy.deepcopy(minimal_community)
    data = {}
    res = client.post(f"/communities/{id_}/rename", headers=headers, json=data)
    assert res.status_code == 400
    assert res.json["errors"][0]["messages"][0] == "Missing data for required field."

    new_id = "Renamed_comm"
    data["slug"] = new_id
    res = client.post(f"/communities/{id_}/rename", headers=headers, json=data)
    assert res.status_code == 200
    assert res.json["slug"] == new_id.lower()

    # UUID is invalid
    minimal_community["slug"] = str(uuid4())
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 400


def test_featured_communities(
    client, location, minimal_community, headers, db, search_clear, admin
):
    """Test featured communities endpoints."""
    client = admin.login(client)

    minimal_community["slug"] = "comm_id"
    res = client.post("/communities", headers=headers, json=minimal_community)
    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    c_id_ = created_community["id"]
    Member.index.refresh()

    # Fetch featured communities
    res = client.get("/communities/featured", headers=headers, json=minimal_community)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0
    _assert_single_item_search(res)

    # Other endpoints are currently only accessible with superuser-access
    # At least we know if the endpoints are accessible and params are provided
    res = client.get(f"/communities/{c_id_}/featured", headers=headers)
    assert res.status_code == 403

    res = client.post(f"/communities/{c_id_}/featured", headers=headers, json={})
    assert res.status_code == 403

    # featured entry does not exist
    res = client.put(f"/communities/{c_id_}/featured/0", headers=headers, json={})
    assert res.status_code == 404

    res = client.delete(f"/communities/{c_id_}/featured/0", headers=headers)
    assert res.status_code == 404


def test_simple_flow_restricted_community(
    app,
    client,
    location,
    minimal_restricted_community_1,
    minimal_restricted_community_2,
    headers,
    owner,
    db,
):
    """Test a simple REST API flow."""
    client = owner.login(client)

    # Create a community
    res = client.post(
        "/communities", headers=headers, json=minimal_restricted_community_1
    )
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)
    created_community = res.json
    id_ = created_community["id"]
    slug = created_community["slug"]

    # Read the community
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["metadata"] == created_community["metadata"]

    read_community = res.json
    Community.index.refresh()

    app.config["COMMUNITIES_ALLOW_RESTRICTED"] = False

    # Create a new community, which should default to public
    res = client.post(
        "/communities", headers=headers, json=minimal_restricted_community_2
    )
    Member.index.refresh()

    assert res.status_code == 403


def test_permissions_modify_community_visibility(
    app,
    client,
    location,
    minimal_community,
    headers,
    owner,
    db,
):
    """Test modifying community visibility."""

    app.config["COMMUNITIES_ALLOW_RESTRICTED"] = False

    client = owner.login(client)
    # Create a public community
    res = client.post("/communities", headers=headers, json=minimal_community)
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)

    created_community = res.json
    id_ = created_community["id"]
    slug = created_community["slug"]

    # Read the community
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["metadata"] == created_community["metadata"]

    read_community = res.json
    Community.index.refresh()

    # try to change public community to restricted
    data = copy.deepcopy(read_community)
    data["metadata"]["title"] = "New title"
    data["access"]["visibility"] = "restricted"
    res = client.put(f"/communities/{id_}", headers=headers, json=data)
    assert res.status_code == 403

    # try to change other attributes but leave the visibility the same
    # happens on community settings page
    data["metadata"]["title"] = "New title 2"
    data["access"]["visibility"] = "public"
    res = client.put(f"/communities/{id_}", headers=headers, json=data)
    assert res.status_code == 200


def test_permissions_modify_community_to_public(
    app,
    client,
    location,
    minimal_restricted_community_1,
    headers,
    owner,
    db,
):
    """Test modifying community visibility."""
    app.config["COMMUNITIES_ALLOW_RESTRICTED"] = True
    client = owner.login(client)
    # Create a public community
    res = client.post(
        "/communities", headers=headers, json=minimal_restricted_community_1
    )
    Member.index.refresh()

    assert res.status_code == 201
    _assert_single_item_response(res)

    created_community = res.json
    id_ = created_community["id"]
    slug = created_community["slug"]

    # Read the community
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["metadata"] == created_community["metadata"]

    read_community = res.json
    Community.index.refresh()
    app.config["COMMUNITIES_ALLOW_RESTRICTED"] = False

    # try to change public community to restricted
    data = copy.deepcopy(read_community)
    data["metadata"]["title"] = "New title"
    data["access"]["visibility"] = "public"
    res = client.put(f"/communities/{id_}", headers=headers, json=data)
    assert res.status_code == 403
