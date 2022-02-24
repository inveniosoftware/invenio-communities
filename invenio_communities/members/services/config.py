# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Service Config."""

from invenio_records_resources.services import Link, RecordServiceConfig

from ..records import Member
from .permissions import CommunityMembersPermissionPolicy
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

    record_cls = Member
    schema = MemberSchema

    permission_policy_cls = CommunityMembersPermissionPolicy
    # result_item_cls = RequestEventItem

    # ResultItem configurations
    links_item = {
        "self": MemberLink("{+api}/communities/{community_id}/members/{entity}/{id}"),  # noqa
    }
    # TODO
    # links_search = pagination_links("{+api}/requests/{request_id}/timeline{?args*}")  # noqa
