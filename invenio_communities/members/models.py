# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community database models."""

from __future__ import absolute_import, print_function

from enum import Enum

from flask_babelex import gettext
from invenio_accounts.models import User
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.models import RecordMetadataBase
from speaklater import make_lazy_gettext
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils.types import ChoiceType, UUIDType

from invenio_communities.requests.models import Request

from .errors import CommunityMemberAlreadyExists

_ = make_lazy_gettext(lambda: gettext)

COMMUNITY_MEMBER_TITLES = {
    'MEMBER': _('Member'),
    'ADMIN': _('Admin'),
    'CURATOR': _('Curator')
}


class CommunityMemberRole(Enum):
    """Constants for possible roles of any given Community member."""
    # TODO Make roles configurable.
    MEMBER = 'M'
    """Member of the community."""

    ADMIN = 'A'
    """Admin of the community."""

    CURATOR = 'C'
    """Curator of the community."""

    @property
    def title(self):
        """Return human readable title."""
        return COMMUNITY_MEMBER_TITLES[self.name]

    @classmethod
    def from_str(cls, val):
        return getattr(cls, val.upper())


COMMUNITY_MEMBER_STATUS = {
    'PENDING': _('Pending'),
    'ACCEPTED': _('Accepted'),
    'REJECTED': _('Rejected'),
    'BLOCKED': _('Blocked')
}


class CommunityMemberStatus(Enum):
    """Community-member relationship status."""

    PENDING = 'P'
    ACCEPTED = 'A'
    REJECTED = 'R'
    BLOCKED = 'B'

    @property
    def title(self):
        """Return human readable title."""
        return COMMUNITY_MEMBER_STATUS[self.name]

    @classmethod
    def from_str(cls, val):
        return getattr(cls, val.upper())


class CommunityMember(db.Model, RecordMetadataBase):
    """Represent a community member role."""

    __tablename__ = 'communities_members'
    __versioned__ = {'versioning': False}
    __table_args__ = (
        db.Index(
            'uidx_community_pid_id_user_id_invitation_id',
            # TODO: Check if this combination would be enough (since user_id can be NULL)
            'community_pid_id', 'user_id',
            # 'community_pid_id', 'user_id', 'invitation_id',
            unique=True,
        ),
        db.Index(
            'uidx_community_pid_id_invitation_id',
            'community_pid_id', 'invitation_id',
            unique=True,
        ),
        {'extend_existing': True},
    )

    community_pid_id = db.Column(
        db.Integer,
        db.ForeignKey(PersistentIdentifier.id),
        nullable=False,
    )
    """Community PID ID."""

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
    )
    """User ID."""

    request_id = db.Column(
        UUIDType,
        db.ForeignKey(Request.id),
        # TODO: should we also allow CommunityMembers without a request?
        nullable=True,
    )
    """Request ID."""

    invitation_id = db.Column(
        db.String(255),
        nullable=True,
    )
    """Invitation ID."""

    status = db.Column(
        ChoiceType(CommunityMemberStatus, impl=db.CHAR(1)),
        nullable=False,
        default=CommunityMemberStatus.PENDING,
    )

    role = db.Column(
        ChoiceType(CommunityMemberRole, impl=db.CHAR(1)), nullable=False)

    user = db.relationship(User, backref='communities')

    community_pid = db.relationship(PersistentIdentifier)

    request = db.relationship(Request)

    @classmethod
    def create(cls, community_pid_id, request_id=None, role='M', status='P',
               user_id=None, invitation_id=None, json=None):
        """Create Community Membership Role."""
        try:
            with db.session.begin_nested():
                obj = cls(
                    community_pid_id=community_pid_id,
                    user_id=user_id,
                    request_id=request_id,
                    invitation_id=invitation_id,
                    role=role,
                    status=status,
                    json=json,
                )
                db.session.add(obj)
        except IntegrityError as ex:
            # TODO: Differentiate between the two possible unique constraint errors
            # that the DB might raise
            raise CommunityMemberAlreadyExists(
                pid_id=community_pid_id,
                user_id=user_id,
                invitation_id=invitation_id,
            )
        return obj

    @classmethod
    def delete(cls, community_member):
        """Delete community member relationship."""
        with db.session.begin_nested():
            db.session.delete(community_member)
