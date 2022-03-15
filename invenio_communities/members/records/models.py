# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Member Model."""

import uuid

from invenio_accounts.models import Role, User
from invenio_db import db
from invenio_records.models import RecordMetadataBase
from invenio_requests.records.models import RequestMetadata
from sqlalchemy import CheckConstraint, Index
from sqlalchemy_utils.types import UUIDType

from ...communities.records.models import CommunityMetadata


class MemberModel(db.Model, RecordMetadataBase):
    """Member model.

    We restrict deletion of users/groups if they are present in the member
    table, to ensure that we have at least one owner. I.e. users must first
    be removed from memberships before they can be deleted, ensuring that
    another owner is set of a community if they are the sole owner.
    """

    __tablename__ = "communities_members"
    __table_args__ = (
        Index('ix_community_user', 'community_id', 'user_id', unique=True),
        Index('ix_community_group', 'community_id', 'group_id', unique=True),
        # Make sure user or group is set but not both.
        CheckConstraint(
            '(user_id IS NULL AND group_id IS NOT NULL) OR '
            '(user_id IS NOT NULL AND group_id IS NULL)',
            name='user_or_group',
        ),
    )

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    community_id = db.Column(
        UUIDType,
        db.ForeignKey(CommunityMetadata.id, ondelete="CASCADE"),
        nullable=False
    )

    role = db.Column(db.String(50), nullable=False)

    active = db.Column(db.Boolean(), index=True, nullable=False)

    visible = db.Column(db.Boolean(), nullable=False)

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="RESTRICT"),
        nullable=True,
    )

    group_id = db.Column(
        db.Integer(),
        db.ForeignKey(Role.id, ondelete="RESTRICT"),
        nullable=True,
    )

    request_id = db.Column(
        UUIDType,
        db.ForeignKey(RequestMetadata.id, ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    """An associated request.

    A request can only be associated with one membership/invitation.
    """

    @classmethod
    def query_memberships(cls, user_id=None, group_ids=None, active=True):
        """Query for (community,role)-pairs."""
        q = db.session.query(
            cls.community_id, cls.role
        ).filter(cls.active==active)

        if user_id:
            q = q.filter(cls.user_id==user_id)
        if group_ids:
            q = q.filter(cls.group_id.in_(group_ids))

        return q.distinct()

    @classmethod
    def count_members(cls, community_id, role=None, active=True):
        """Count number of members."""
        q = cls.query.filter(
            cls.community_id==community_id,
            cls.active==active
        )
        if role is not None:
            q = q.filter(cls.role==role)
        return q.count()

