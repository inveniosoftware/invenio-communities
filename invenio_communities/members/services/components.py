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

from ...utils import on_membership_change


class CommunityMemberCachingComponent(ServiceComponent):
    """Service component for community member caching."""

    def _member_changed(self, member):
        """Call caching membership change function for user."""

        def _get_user_ids_from_group_id(role_id):
            r = Role.query.filter(Role.id == role_id).one()
            return [u.id for u in r.users.all()]

        user_ids = []
        if isinstance(member, MemberMixin):
            if member.user_id:
                user_ids = [member.user_id]
            elif member.group_id:
                user_ids = _get_user_ids_from_group_id(member.group_id)
            else:
                return
        elif isinstance(member, dict):
            if member.get("type") == "user":
                user_ids = [member["id"]]
            elif member.get("type") == "group":
                user_ids = _get_user_ids_from_group_id(member["id"])
            else:
                return
        else:
            raise TypeError(
                "Member must be 'MemberMixin' or 'dict' but was {type}".format(
                    type=type(member)
                )
            )

        for user_id in user_ids:
            on_membership_change(Identity(user_id))

    def accept_invite(self, identity, record=None, data=None, **kwargs):
        """On accept invite."""
        self._member_changed(record)

    def members_add(self, identity, record=None, data=None, **kwargs):
        """On member add (only for groups)."""
        self._member_changed(record)

    def members_delete(self, identity, record=None, data=None, **kwargs):
        """On member delete."""
        self._member_changed(record)

    def members_update(self, identity, record=None, data=None, **kwargs):
        """On member update."""
        self._member_changed(record)
