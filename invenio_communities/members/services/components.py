# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Members Components."""

from flask_principal import Identity
from invenio_accounts.models import Role
from invenio_records_resources.services.records.components import ServiceComponent

from invenio_communities.members.records.api import MemberMixin

from ...proxies import current_identities_cache
from ...utils import on_group_membership_change, on_user_membership_change


class CommunityMemberCachingComponent(ServiceComponent):
    """Service component for community member caching."""

    def _member_changed(self, member, community=None):
        """Call caching membership change function for user."""
        user_ids = []
        if isinstance(member, MemberMixin):
            if member.user_id:
                user_ids = [member.user_id]
            elif member.group_id:
                if not community:
                    raise TypeError("Community must be defined.")
                on_group_membership_change(str(community.id))
            else:
                return
        elif isinstance(member, dict):
            if member.get("type") == "user":
                user_ids = [member["id"]]
            elif member.get("type") == "group":
                if not community:
                    raise TypeError("Community must be defined.")
                on_group_membership_change(str(community.id))
            else:
                return
        else:
            raise TypeError(
                "Member must be 'MemberMixin' or 'dict' but was {type}".format(
                    type=type(member)
                )
            )

        for user_id in user_ids:
            on_user_membership_change(Identity(user_id))

    def accept_invite(self, identity, record=None, data=None, **kwargs):
        """On accept invite."""
        self._member_changed(record)

    def members_add(self, identity, record=None, community=None, data=None, **kwargs):
        """On member add (only for groups)."""
        if record["type"] == "group":
            role = Role.query.filter_by(id=record["id"]).one_or_none()
            if role.is_managed:
                users = role.users.all()
                for user in users:
                    on_user_membership_change(Identity(user.id))
            else:
                current_identities_cache.flush()
        elif record["type"] == "user":
            self._member_changed(record)

    def members_delete(
        self, identity, record=None, community=None, data=None, **kwargs
    ):
        """On member delete."""
        self._member_changed(record, community=community)

    def members_update(
        self, identity, record=None, community=None, data=None, **kwargs
    ):
        """On member update."""
        self._member_changed(record, community=community)
