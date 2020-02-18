# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record database models."""

from __future__ import absolute_import, print_function

import uuid
from enum import Enum

from flask_babelex import gettext
from invenio_db import db
from invenio_records.models import RecordMetadataBase
from invenio_accounts.models import User
from speaklater import make_lazy_gettext
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils.types import ChoiceType, UUIDType

from invenio_communities.models import CommunityMetadata
# TODO make sure well what this does and that we need this dependency
_ = make_lazy_gettext(lambda: gettext)


class CommunityRecordAlreadyExists(Exception):
    """Record inclusion already exists error."""

    def __init__(self, user_id, pid_id, pid_type):
        """Initialize Exception."""
        self.user_id = user_id
        self.pid_id = pid_id
        self.pid_type = pid_type


class CommunityRecordDoesNotExist(CommunityRecordAlreadyExists):
    """Record inclusion does not exist error."""

    pass


COMMUNITY_RECORD_STATUS = {
    'ACCEPTED': _('Accepted'),
    'REJECTED': _('Rejected'),
    'PENDING': _('Pending'),
    'REMOVED': _('Removed'),
    'CANCELLED': _('Cancelled')
}


class CommunityRecordStatus(Enum):
    """Constants for possible states of a community record inclusion."""

    ACCEPTED = 'A'

    REJECTED = 'R'

    PENDING = 'P'

    REMOVED = 'D'

    CANCELLED = 'D'

    @property
    def title(self):
        """Return human readable title."""
        return COMMUNITY_RECORD_STATUS[self.name]


class CommunityRecordInclusion(db.Model, RecordMetadataBase):
    """Represent a record member."""

    __tablename__ = 'community_record_inclusion'
    __table_args__ = {'extend_existing': True}
    __versioned__ = {'versioning': False}

    id = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )

    "Record PID ID"
    pid_type = db.Column(
        UUIDType,
        nullable=False,
    )

    pid_value = db.Column(
        UUIDType,
        nullable=False,
    )

    comm_id = db.Column(
        UUIDType,
        db.ForeignKey(CommunityMetadata.id),
        nullable=False,
    )

    status = db.Column(
        ChoiceType(CommunityRecordStatus, impl=db.CHAR(1)), nullable=False)

    is_invite = db.Column(db.Boolean(name='is_invite'), nullable=False,
                          default=True)

    owner_id = db.Column(
        UUIDType,
        db.ForeignKey(User.id),
        nullable=False,
    )

    communities = db.relationship(CommunityMetadata, backref='records')
    user = db.relationship(User, backref='community_records')

    @classmethod
    def create(cls, comm_id, is_invite, pid_value, pid_type, status):
        """Create Record Membership request."""
        try:
            with db.session.begin_nested():
                obj = cls(
                    comm_id=comm_id, is_invite=is_invite, pid_value=pid_value,
                    pid_type=pid_type, status=status)
                db.session.add(obj)
        except IntegrityError:
            raise CommunityRecordAlreadyExists(
                comm_id=comm_id, pid_value=pid_value, pid_type=pid_type)
        return obj

    @classmethod
    def delete(cls, inclusion_id, force=False):
        """Delete a record inclusion request."""
        try:
            with db.session.begin_nested():
                inclusion = cls.query.get(inclusion_id)
                db.session.delete(inclusion)
        except IntegrityError:
            raise CommunityRecordDoesNotExist(id)

    @classmethod
    def get_records(cls, comm_id):
        """Get all the records of a community."""
        return cls.query.filter_by(comm_id=comm_id,)
