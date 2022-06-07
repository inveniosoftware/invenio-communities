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
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils.types import UUIDType

from ...communities.records.models import CommunityMetadata


class BaseMemberModel(RecordMetadataBase):
    """
    Base model for members, invitations and archived invitations.

    We restrict deletion of users/groups if they are present in the member
    table, to ensure that we have at least one owner. I.e. users must first
    be removed from memberships before they can be deleted, ensuring that
    another owner is set of a community if they are the sole owner.
    """

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    @declared_attr
    def community_id(cls):
        """Foreign key to the related community."""
        return db.Column(
            UUIDType,
            db.ForeignKey(CommunityMetadata.id, ondelete="CASCADE"),
            nullable=False,
        )

    role = db.Column(db.String(50), nullable=False)

    visible = db.Column(db.Boolean(), nullable=False)

    @declared_attr
    def user_id(cls):
        """Foreign key to the related user."""
        return db.Column(
            db.Integer(),
            db.ForeignKey(User.id, ondelete="RESTRICT"),
            nullable=True,
        )

    @declared_attr
    def group_id(cls):
        """Foreign key to the related group."""
        return db.Column(
            db.Integer(),
            db.ForeignKey(Role.id, ondelete="RESTRICT"),
            nullable=True,
        )

    @declared_attr
    def request_id(cls):
        """Foreign key to the related request.

        A request can only be associated with one membership/invitation.
        """
        return db.Column(
            UUIDType,
            db.ForeignKey(RequestMetadata.id, ondelete="SET NULL"),
            nullable=True,
            unique=True,
        )

    active = db.Column(db.Boolean(), index=True, nullable=False)

    @classmethod
    def query_memberships(cls, user_id=None, group_ids=None, active=True):
        """Query for (community,role)-pairs."""
        q = db.session.query(cls.community_id, cls.role).filter(cls.active == active)

        if user_id:
            q = q.filter(cls.user_id == user_id)
        if group_ids:
            q = q.filter(cls.group_id.in_(group_ids))

        return q.distinct()

    @classmethod
    def count_members(cls, community_id, role=None, active=True):
        """Count number of members."""
        q = cls.query.filter(cls.community_id == community_id, cls.active == active)
        if role is not None:
            q = q.filter(cls.role == role)
        return q.count()


class MemberModel(db.Model, BaseMemberModel):
    """Member and invitation model.

    We store members and invitations in the same table to two reasons:

    1. Reduced table size: The table is queried on login for all memberships
       of a user, and thus a smaller size is preferable.

    2. Mixing members and invitations ensures we can easily check integrity
       constraints. E.g. it's not possible to invite an existing member, and
       a person can only be invited once (database insertion will fail).
    """

    __tablename__ = "communities_members"
    __table_args__ = (
        Index("ix_community_user", "community_id", "user_id", unique=True),
        Index("ix_community_group", "community_id", "group_id", unique=True),
        # Make sure user or group is set but not both.
        CheckConstraint(
            "(user_id IS NULL AND group_id IS NOT NULL) OR "
            "(user_id IS NOT NULL AND group_id IS NULL)",
            name="user_or_group",
        ),
    )


class ArchivedInvitationModel(db.Model, BaseMemberModel):
    """Archived invitations model.

    The archived invitations model stores invitations that was rejected or
    cancelled, to support the use case of seeing if invitations was rejected
    or cancelled, and seeing past invitations.
    """

    __tablename__ = "communities_archivedinvitations"

    # We're not adding a check constraint since the row has already been
    # inserted in the member model where it was checked.

    @classmethod
    def from_member_model(cls, member_model):
        """Create an archived invitation model from a member model."""
        # Note, we keep the "active" model field, because it makes it easier to
        # handle with the search index, when we search over a combined
        # search alias for members/invitations and archived invitations.
        assert member_model.active is False
        return cls(
            id=member_model.id,
            community_id=member_model.community_id,
            user_id=member_model.user_id,
            group_id=member_model.group_id,
            request_id=member_model.request_id,
            role=member_model.role,
            visible=member_model.visible,
            active=member_model.active,
            created=member_model.created,
            updated=member_model.updated,
            version_id=member_model.version_id,
        )
