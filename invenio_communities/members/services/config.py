# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Service Config."""

from invenio_records_resources.services import Link, RecordServiceConfig

from ...communities.records.api import Community
from ...permissions import CommunityPermissionPolicy
from ..records import Member
from .schema import MemberSchema


class MemberLink(Link):
    """Link variables setter for RequestEvent links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        # TODO: Revise for human-readable community id and different entities.
        vars.update({
            "community_id": record.community_id,
            "entity": "user",
            "id": record.user_id,
        })


class MemberServiceConfig(RecordServiceConfig):
    """Member Service Config."""

    community_cls = Community
    record_cls = Member
    schema = MemberSchema

    permission_policy_cls = CommunityPermissionPolicy
    # result_item_cls = RequestEventItem

    # ResultItem configurations
    links_item = {
        "self": MemberLink("{+api}/communities/{community_id}/members/{entity}/{id}"),  # noqa
    }
    # TODO
    # links_search = pagination_links("{+api}/requests/{request_id}/timeline{?args*}")  # noqa
