# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Abstract database model for modelling community/record relationships."""

from invenio_db import db
from invenio_requests.records.models import RequestMetadata
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils.types import UUIDType

from ...communities.records.models import CommunityMetadata


class CommunityRelationMixin:
    """Model mixin to define a relationship between a communities and records.

    Usage:

    .. code-block:: python

        class CommunityRecordM2M(db.Model, CommunityRelationMixin):
            __record_model__ = MyParentRecord
    """

    __record_model__ = None
    __request_model__ = None

    @declared_attr
    def community_id(cls):
        """Foreign key to the related communithy."""
        return db.Column(
            UUIDType,
            db.ForeignKey(CommunityMetadata.id, ondelete="CASCADE"),
            primary_key=True,
        )

    @declared_attr
    def record_id(cls):
        """Foreign key to the related record."""
        return db.Column(
            UUIDType,
            db.ForeignKey(cls.__record_model__.id, ondelete="CASCADE"),
            primary_key=True,
        )

    @declared_attr
    def request_id(cls):
        """Foreign key to a related request."""
        return db.Column(
            UUIDType,
            db.ForeignKey(RequestMetadata.id, ondelete="SET NULL"),
            nullable=True,
        )
