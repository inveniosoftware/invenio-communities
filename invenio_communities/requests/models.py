# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Requests database models."""

from __future__ import absolute_import, print_function

import uuid

from invenio_accounts.models import User
from invenio_db import db
from invenio_records.models import RecordMetadataBase, Timestamp
from sqlalchemy.dialects import mysql
from sqlalchemy_utils.types import UUIDType


# TODO: Move to invenio-requests
class Request(db.Model, RecordMetadataBase):
    """Requests model."""

    __tablename__ = 'requests_request'
    __table_args__ = {'extend_existing': True}
    __versioned__ = {'versioning': False}

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
    )

    expires_at = db.Column(
        db.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
    )

    cancelled_at = db.Column(
        db.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
    )

    sla = db.Column(
        db.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
    )

    routing_key = db.Column(
        db.String(255),
    )

    owner = db.relationship(
        User,
        backref='requests',
    )

    @classmethod
    def delete(cls, request):
        """Delete request."""
        with db.session.begin_nested():
            db.session.delete(request)


class Comment(db.Model, Timestamp):
    """Comment in a request."""

    __tablename__ = 'requests_comment'

    id = db.Column(
        UUIDType,
        default=uuid.uuid4,
        primary_key=True,
    )

    request_id = db.Column(
        UUIDType,
        db.ForeignKey(Request.id, ondelete="CASCADE"),
        nullable=False,
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        nullable=False
    )

    message = db.Column(db.Text)

    request = db.relationship(
        Request,
        backref=db.backref(
            'comments',
            cascade='all, delete-orphan',
            passive_deletes=True,
        ),
    )

    @classmethod
    def create(cls, request_id, created_by, message):
        with db.session.begin_nested():
            obj = cls(
                request_id=request_id,
                created_by=created_by,
                message=message,
            )
            db.session.add(obj)
        return obj
