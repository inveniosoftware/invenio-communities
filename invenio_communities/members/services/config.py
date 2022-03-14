# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Service Config."""

from invenio_records_resources.services import Link, RecordServiceConfig, \
    pagination_links

from ...communities.records.api import Community
from ...permissions import CommunityPermissionPolicy
from ..records import Member
from .schemas import MemberSchema


class MemberLink(Link):
    """Link variables setter for RequestEvent links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update({
            "member_id": record.id,
        })


class MemberServiceConfig(RecordServiceConfig):
    """Member Service Config."""

    community_cls = Community
    record_cls = Member
    schema = MemberSchema

    permission_policy_cls = CommunityPermissionPolicy

    # ResultItem configurations
    links_item = {
        "self": MemberLink("{+api}/communities/{community_id}/members/{member_id}"),  # noqa
    }

    # ResultList configurations
    links_search = pagination_links(
        "{+api}/communities/{community_id}/members{?args*}"
    )
