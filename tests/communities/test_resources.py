# SPDX-FileCopyrightText: 2016-2024 CERN.
# SPDX-FileCopyrightText: 2022 Northwestern University.
# SPDX-License-Identifier: MIT

"""Community resources tests."""

import copy
import hashlib
from io import BytesIO
from uuid import uuid4

from invenio_access.permissions import system_identity

from invenio_communities.communities.entity_resolvers import pick_fields
from invenio_communities.communities.records.api import Community
from invenio_communities.members import Member
from invenio_communities.proxies import current_communities


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
        "record_submission_policy",
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
    res = client.get("/communities", query_string={"q": f"id:{id_}"}, headers=headers)
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
    res = client.get("/communities", query_string={"q": f"id:{id_}"}, headers=headers)
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
    res = client.get("/communities", query_string={"q": ""}, headers=headers)
    assert res.status_code == 200
    _assert_single_item_search(res)
    assert res.json["hits"]["total"] == total
    assert res.json["hits"]["hits"][0]["slug"] == slug_newest
    assert res.json["hits"]["hits"][0]["metadata"] == community_copy["metadata"]

    # Search filter for the second commmunity
    res = client.get(
        "/communities", query_string={"q": "metadata.type.id:project"}, headers=headers
    )
    assert res.status_code == 200
    _assert_single_item_search(res)
    assert res.json["hits"]["total"] == num_each

    # Sort results by oldest
    res = client.get(
        "/communities", query_string={"q": "", "sort": "oldest"}, headers=headers
    )
    assert res.status_code == 200
    assert res.json["hits"]["hits"][0]["slug"] == slug_oldest

    # Test for page and size
    res = client.get(
        "/communities",
        query_string={"q": "", "size": "5", "page": "2"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == total
    assert len(res.json["hits"]["hits"]) == 5

    # Test search for prefix
    res = client.get("/communities", query_string={"q": "Comm"}, headers=headers)
    assert res.status_code == 200
    _assert_single_item_search(res)
    assert res.json["hits"]["total"] == total  # they all have the name "My Community"


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
        "record_submission_policy": "closed",
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
        "record_submission_policy": "closed",
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
    assert created_community["logo"] is None
    assert "logo" not in created_community["links"]
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
    assert (
        res.json["links"]["self"]
        == f"https://127.0.0.1:5000/api/communities/{id_}/logo"
    )

    # Logo state and versioned link are on the community, in DB reads and search
    checksum = f"md5:{hashlib.md5(b'logo').hexdigest()}"
    logo_link = f"https://127.0.0.1:5000/api/communities/{id_}/logo?v={checksum}"
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.json["logo"] == {"checksum": checksum, "size": 4}
    assert res.json["links"]["logo"] == logo_link
    Community.index.refresh()
    res = client.get("/communities", headers=headers, query_string={"q": f"id:{id_}"})
    hit = res.json["hits"]["hits"][0]
    assert hit["logo"] == {"checksum": checksum, "size": 4}
    assert hit["links"]["logo"] == logo_link

    # Get logo
    res = client.get(f"/communities/{id_}/logo")
    assert res.status_code == 200
    assert res.data == b"logo"
    assert "immutable" not in res.headers.get("Cache-Control", "")

    # Versioned URL is cached forever
    res = client.get(f"/communities/{id_}/logo", query_string={"v": checksum})
    assert res.status_code == 200
    assert res.cache_control.public
    assert res.cache_control.immutable
    assert res.cache_control.max_age == 31536000

    # Stale version is not cached
    res = client.get(f"/communities/{id_}/logo", query_string={"v": "md5:stale"})
    assert res.status_code == 200
    assert not res.cache_control.immutable

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
    new_checksum = f"md5:{hashlib.md5(b'new_logo').hexdigest()}"
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.json["logo"] == {"checksum": new_checksum, "size": 8}
    assert res.json["links"]["logo"].endswith(f"?v={new_checksum}")

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
    res = client.get(f"/communities/{id_}", headers=headers)
    assert res.json["logo"] is None
    assert "logo" not in res.json["links"]
    Community.index.refresh()
    res = client.get("/communities", headers=headers, query_string={"q": f"id:{id_}"})
    assert "logo" not in res.json["hits"]["hits"][0]["links"]

    # TODO: Delete community and try all of the above operations


def test_logo_state_missing_from_dump(
    app, client, location, minimal_community, headers, db, search_clear, owner
):
    """Old documents without logo state are assumed to have a logo while reindexing."""
    client = owner.login(client)
    res = client.post("/communities", headers=headers, json=minimal_community)
    record = Community.get_record(res.json["id"])

    dump = record.dumps()
    assert dump["logo"] == {"exists": False}
    assert Community.loads(dict(dump)).logo.exists is False
    del dump["logo"]
    loaded = Community.loads(dump)
    assert loaded.logo.exists is True
    assert loaded.logo.checksum is None


def test_logo_entity_resolver_links(
    app, client, location, minimal_community, headers, db, search_clear, owner
):
    """Expanded communities only link a logo that exists or may exist."""
    client = owner.login(client)
    res = client.post("/communities", headers=headers, json=minimal_community)
    community = current_communities.service.read(system_identity, res.json["id"])
    community_dict = community.to_dict()
    assert community_dict["logo"] is None
    assert pick_fields(system_identity, community_dict)["links"] == {}

    del community_dict["logo"]
    links = pick_fields(system_identity, community_dict)["links"]
    assert links["logo"].endswith(f"/communities/{res.json['id']}/logo")

    client.put(
        f"/communities/{res.json['id']}/logo",
        headers={"content-type": "application/octet-stream"},
        data=BytesIO(b"logo"),
    )
    community_dict = current_communities.service.read(
        system_identity, res.json["id"]
    ).to_dict()
    checksum = f"md5:{hashlib.md5(b'logo').hexdigest()}"
    assert community_dict["logo"] == {"checksum": checksum, "size": 4}
    links = pick_fields(system_identity, community_dict)["links"]
    assert links["logo"].endswith(f"/logo?v={checksum}")


def test_logo_search_filter(
    app, client, location, minimal_community, headers, db, search_clear, owner
):
    """Communities can be filtered by whether they have a logo."""
    client = owner.login(client)
    res = client.post("/communities", headers=headers, json=minimal_community)
    community_id = res.json["id"]
    Community.index.refresh()

    def search(q):
        res = client.get("/communities", query_string={"q": q}, headers=headers)
        return [hit["id"] for hit in res.json["hits"]["hits"]]

    assert search("logo.exists:false") == [community_id]
    assert search("logo.exists:true") == []

    client.put(
        f"/communities/{community_id}/logo",
        headers={"content-type": "application/octet-stream"},
        data=BytesIO(b"logo"),
    )
    Community.index.refresh()
    assert search("logo.exists:true") == [community_id]
    assert search("logo.exists:false") == []


def test_logo_field(
    app, client, location, minimal_community, headers, db, search_clear, owner
):
    """Setting, replacing and deleting the logo through the record field."""
    client = owner.login(client)
    res = client.post("/communities", headers=headers, json=minimal_community)
    record = Community.get_record(res.json["id"])
    assert record.logo.exists is False
    assert record.logo.file is None

    record.logo = BytesIO(b"logo")
    assert record.logo.exists is True
    assert record.logo.checksum == f"md5:{hashlib.md5(b'logo').hexdigest()}"
    assert record.logo.size == 4
    assert record.logo.file.key == "logo"

    record.logo = BytesIO(b"new_logo")
    assert record.logo.size == 8

    del record.logo
    assert record.logo.exists is False
    assert record.logo.file is None
    assert "logo" not in record.files

    record.logo = BytesIO(b"logo")
    record.logo = None
    assert record.logo.exists is False
    assert "logo" not in record.files
    assert "logo" not in record


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
    assert "logo" not in created_community["links"]
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
    assert (
        res.json["message"] == "Logo size limit exceeded. Limit: 1.00 MB Given: 4.00 MB"
    )

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
        == "The identifier should contain only letters, numbers, or dashes."
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
        == "The identifier should contain only letters, numbers, or dashes."
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
    client, location, minimal_community, headers, db, search_clear, owner, admin
):
    """Test featured communities endpoints."""
    client = owner.login(client)
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

    # Feature action is only allowed for admin
    res = client.post(
        f"/communities/{c_id_}/featured",
        headers=headers,
        json={"start_date": "2024-11-28T12:03:53"},
    )
    assert res.status_code == 403
    owner.logout(client)

    # Other endpoints are currently only accessible with admin-access
    client = admin.login(client)
    res = client.get(f"/communities/{c_id_}/featured", headers=headers)
    assert res.status_code == 200

    res = client.post(
        f"/communities/{c_id_}/featured",
        headers=headers,
        json={"start_date": "2024-11-28T12:03:53"},
    )
    assert res.status_code == 201
    feat_id = res.json["id"]

    # update featured entry
    res = client.put(
        f"/communities/{c_id_}/featured/{feat_id}",
        headers=headers,
        json={"start_date": "2024-12-01T12:03:58"},
    )
    assert res.status_code == 200

    res = client.delete(f"/communities/{c_id_}/featured/{feat_id}", headers=headers)
    assert res.status_code == 204


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
