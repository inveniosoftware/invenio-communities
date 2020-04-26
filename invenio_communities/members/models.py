# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community database models."""

from __future__ import absolute_import, print_function

import uuid
from enum import Enum

from flask_babelex import gettext
from invenio_accounts.models import User
from invenio_db import db
from speaklater import make_lazy_gettext
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils.types import ChoiceType, UUIDType

from invenio_communities.models import CommunityMetadata

# TODO make sure well what this does and that we need this dependency
_ = make_lazy_gettext(lambda: gettext)


class CommunityMemberAlreadyExists(Exception):
    """Community membership already exists error."""

    def __init__(self, user_id, pid_id, role):
        """Initialize Exception."""
        self.user_id = user_id
        self.pid_id = pid_id
        self.role = role


class CommunityMemberDoesNotExist(CommunityMemberAlreadyExists):
    """Community membership does not exist error."""

    pass


COMMUNITY_MEMBER_TITLES = {
    'MEMBER': _('Member'),
    'ADMIN': _('Admin'),
    'CURATOR': _('Curator')
}


class CommunityRoles(Enum):
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


class CommunityMember(db.Model):
    """Represent a community member role."""

    __tablename__ = 'communities_members'

    "Community PID ID"
    comm_id = db.Column(
        UUIDType,
        db.ForeignKey(CommunityMetadata.id),
        primary_key=True,
        nullable=False,
    )

    "USER ID"
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        primary_key=True,
        nullable=False,
    )

    role = db.Column(
        ChoiceType(CommunityRoles, impl=db.CHAR(1)), nullable=False)

    user = db.relationship(User, backref='communities')

    community = db.relationship(CommunityMetadata, backref='members')

    @property
    def email(self):
        """Get user email."""
        return self.user.email

    @classmethod
    def create_from_object(cls, membership_request):
        """Create Community Membership Role."""
        with db.session.begin_nested():
            obj = cls.create(
                comm_id=membership_request.comm_id,
                user_id=membership_request.user_id,
                role=membership_request.role)
            db.session.delete(membership_request)
        return obj

    @classmethod
    def create(cls, comm_id, user_id, role):
        """Create Community Membership Role."""
        try:
            with db.session.begin_nested():
                obj = cls(
                    comm_id=comm_id,
                    user_id=user_id,
                    role=role)
                db.session.add(obj)
        except IntegrityError:
            raise CommunityMemberAlreadyExists(
                comm_id=comm_id,
                user_id=user_id,
                role=role)
        return obj

    @classmethod
    def delete(cls, comm_id, user_id):
        """Delete a community membership."""
        try:
            with db.session.begin_nested():
                membership = cls.query.filter_by(
                    comm_id=comm_id, user_id=user_id).one()
                db.session.delete(membership)
        except IntegrityError:
            raise CommunityMemberDoesNotExist(comm_id=comm_id, user_id=user_id)

    @classmethod
    def get_admins(cls, comm_id):
        with db.session.begin_nested():
            return cls.query.filter_by(comm_id=comm_id, role='A').all()

    @classmethod
    def get_members(cls, comm_id):
        with db.session.begin_nested():
            return cls.query.filter_by(comm_id=comm_id)


class MembershipRequest(db.Model):
    """Represent a community member role."""

    __tablename__ = 'communities_membership_request'

    id = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        nullable=True,
    )

    comm_id = db.Column(
        UUIDType,
        db.ForeignKey(CommunityMetadata.id),
        nullable=False,
    )

    email = db.Column(
        db.String(255),
        nullable=True,
    )

    role = db.Column(
        ChoiceType(CommunityRoles, impl=db.CHAR(1)), nullable=True)

    is_invite = db.Column(db.Boolean(name='is_invite'), nullable=False,
                          default=True)

    @classmethod
    def create(cls, comm_id, is_invite, role=None, user_id=None, email=None):
        """Create Community Membership request."""
        try:
            with db.session.begin_nested():
                obj = cls(
                    comm_id=comm_id, user_id=user_id,
                    role=role, is_invite=is_invite, email=email)
                db.session.add(obj)
        except IntegrityError:
            raise CommunityMemberAlreadyExists(
                comm_id=comm_id, user_id=user_id, role=role)
        return obj

    @classmethod
    def delete(cls, id):
        """Delete a community membership request."""
        try:
            with db.session.begin_nested():
                membership = cls.query.get(id)
                db.session.delete(membership)
        except IntegrityError:
            raise CommunityMemberDoesNotExist(id)
