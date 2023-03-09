# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from flask import g

from invenio_communities.communities.resources.serializer import (
    UICommunityJSONSerializer,
)


def test_ui_serializer(app, community, users, any_user):
    owner = users["owner"]
    reader = users["reader"]
    closed_review_comm = community.to_dict()
    closed_review_comm["access"]["review_policy"] = "closed"
    closed_review_expected_data = {
        "permissions": {"can_include_directly": False, "can_update": True}
    }

    # set current user to owner
    g.identity = owner.identity

    serialized_record = UICommunityJSONSerializer().dump_obj(closed_review_comm)
    assert (
        serialized_record["ui"]["permissions"]
        == closed_review_expected_data["permissions"]
    )

    open_review_comm = community.to_dict()
    open_review_comm["access"]["review_policy"] = "open"
    open_review_expected_data = {
        "permissions": {"can_include_directly": True, "can_update": True}
    }

    serialized_record = UICommunityJSONSerializer().dump_obj(open_review_comm)
    assert (
        serialized_record["ui"]["permissions"]
        == open_review_expected_data["permissions"]
    )

    # set user to community reader
    g.identity = reader.identity
    require_review_expected_data = {
        "permissions": {"can_include_directly": False, "can_update": False}
    }

    serialized_record = UICommunityJSONSerializer().dump_obj(open_review_comm)
    assert (
        serialized_record["ui"]["permissions"]
        == require_review_expected_data["permissions"]
    )

    # set user to any user
    g.identity = any_user.identity
    serialized_record = UICommunityJSONSerializer().dump_obj(open_review_comm)
    assert (
        serialized_record["ui"]["permissions"]
        == require_review_expected_data["permissions"]
    )
