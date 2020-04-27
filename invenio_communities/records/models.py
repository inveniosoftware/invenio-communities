# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record database models."""

from __future__ import absolute_import, print_function

from enum import Enum

from flask_babelex import gettext
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.models import RecordMetadataBase
from speaklater import make_lazy_gettext
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils.types import ChoiceType, UUIDType

from invenio_communities.models import CommunityMetadata
from invenio_communities.requests.models import Request

from .errors import CommunityRecordAlreadyExists

# TODO make sure well what this does and that we need this dependency
_ = make_lazy_gettext(lambda: gettext)


COMMUNITY_RECORD_STATUS = {
    'PENDING': _('Pending'),
    'ACCEPTED': _('Accepted'),
    'REJECTED': _('Rejected')
}


class CommunityRecordStatus(Enum):
    """Community-record relationship status."""

    PENDING = 'P'
    ACCEPTED = 'A'
    REJECTED = 'R'

    @property
    def title(self):
        """Return human readable title."""
        return COMMUNITY_RECORD_STATUS[self.name]


class CommunityRecord(db.Model, RecordMetadataBase):
    """Comunity-record relationship model."""

    __tablename__ = 'communities_community_record'
    __table_args__ = (
        db.Index(
            'uidx_community_pid_record_pid',
            'community_pid_id', 'record_pid_id',
            unique=True,
        ),
        {'extend_existing': True},
    )
    __versioned__ = {'versioning': False}

    community_pid_id = db.Column(
        db.Integer,
        db.ForeignKey(PersistentIdentifier.id),
        nullable=False,
    )

    record_pid_id = db.Column(
        db.Integer,
        db.ForeignKey(PersistentIdentifier.id),
        nullable=False,
    )

    request_id = db.Column(
        UUIDType,
        db.ForeignKey(Request.id),
        # TODO: should we also allow CommunityRecords without a request?
        nullable=False,
    )

    status = db.Column(
        ChoiceType(CommunityRecordStatus, impl=db.CHAR(1)),
        nullable=False,
        default=CommunityRecordStatus.PENDING,
    )

    community_pid = db.relationship(
        PersistentIdentifier,
        foreign_keys=[community_pid_id],
    )
    record_pid = db.relationship(
        PersistentIdentifier,
        foreign_keys=[record_pid_id],
    )

    request = db.relationship(Request)

    @property
    def commmunity(self):
        """Return community model."""
        # TODO: make a JOIN instead?
        return CommunityMetadata.query.get(self.community_pid.object_uuid)

    @classmethod
    def create(cls, community_pid_id, record_pid_id, request_id,
               status=None, json=None):
        try:
            with db.session.begin_nested():
                # TODO: check if status None works with default
                obj = cls(
                    community_pid_id=community_pid_id,
                    record_pid_id=record_pid_id,
                    request_id=request_id,
                    status=status,
                    json=json,
                )
                db.session.add(obj)
        # TODO: Check if actually this constraint check happens on the DB side
        #       when db.session.add() is called.
        except IntegrityError:
            raise CommunityRecordAlreadyExists(
                community_pid_id=community_pid_id,
                record_pid_id=record_pid_id,
            )
        return obj

    @classmethod
    def delete(cls, community_record):
        """Delete community record relationship."""
        with db.session.begin_nested():
            db.session.delete(community_record)

    # TODO: investigate using RECORDS_PIDS_OBJECT_TYPES or
    #       current_pidstore.resolve
    # @property
    # def record(self)
    #     pass
    #
    # RECORDS_PIDS_OBJECT_TYPES = {
    #     'rec': RecordMetadata,
    #     'com': CommunityMetadata,
    # }
