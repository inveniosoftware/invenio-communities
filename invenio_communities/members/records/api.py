# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"Members data layer API."

from invenio_accounts.models import Role
from invenio_communities.members.errors import InvalidMemberError
from invenio_db import db
from invenio_records.systemfields import ModelField
from invenio_records_resources.records.api import Record
from invenio_records_resources.records.systemfields import IndexField
from sqlalchemy import or_

from .models import MemberModel


class Member(Record):
    """A member record.

    We are using a record without using the actual JSON document and
    schema validation normally used in a record. The reason for using a record
    is to facilitate the indexing which we need to have an effective search
    over the list of members.
    """

    model_cls = MemberModel

    # Systemfields

    metadata = None

    index = IndexField(
        "communitymembers-members-v1.0.0", search_alias="communitymembers"
    )
    """The ES index used."""

    community_id = ModelField("community_id")
    """The data-layer UUID of the community."""

    user_id = ModelField("user_id")
    """The data-layer id of the user (or None)."""

    group_id = ModelField("group_id")
    """The data-layer id of the user (or None)."""

    request_id = ModelField("request_id")
    """The data-layer id of the user (or None)."""

    role = ModelField("role")
    """The role of the entity."""

    visible = ModelField("visible")
    """Visibility of the membership."""

    active = ModelField("active")
    """Determine if it's an active membership.

    This is used for e.g. invitations where a memberships is created but not
    yet activated.
    """

    @classmethod
    def get_memberships(cls, identity):
        """Get community memberships for a given identity."""
        # TODO: extract group/role ids from identity
        query = cls.model_cls.query_memberships(
            user_id=identity.id, group_ids=[]
        )
        return [(str(comm_id), role) for comm_id, role in query]

    @classmethod
    def get_member_by_request(cls, request_id):
        """Get a membership by request id."""
        assert request_id is not None
        obj = cls.model_cls.query.filter(
            cls.model_cls.request_id==request_id
        ).one()
        return cls(obj.data, model=obj)

    @classmethod
    def get_members(cls, community_id, members=None):
        """Get members of a community."""
        # Collect users and groups we are interested in
        user_ids = []
        group_names = []
        for m in (members or []):
            if m['type'] == 'group':
                group_names.append(m['id'])
            elif m['type'] == 'user':
                user_ids.append(m['id'])
            else:
                raise InvalidMemberError(m)

        # Query
        q = cls.model_cls.query.filter(
            cls.model_cls.community_id == community_id
        )

        # Apply user and group query if applicable
        user_q = cls.model_cls.user_id.in_(user_ids)
        groups_q = cls.model_cls.group_id.in_(
            db.session.query(Role.id).filter(Role.name.in_(group_names))
        )
        if user_ids and group_names:
            q = q.filter(or_(user_q, groups_q))
        elif user_ids:
            q = q.filter(user_q)
        elif group_names:
            q = q.filter(groups_q)

        return [cls(obj.data, model=obj) for obj in q.all()]


    @classmethod
    def has_members(cls, community_id, role=None):
        """Get members of a community."""
        return cls.model_cls.count_members(community_id, role=role)
