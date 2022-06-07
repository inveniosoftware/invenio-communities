# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C)      2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community database models."""

from datetime import datetime

from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase, Timestamp
from invenio_records_resources.records import FileRecordModelMixin
from sqlalchemy.dialects import mysql
from sqlalchemy.types import String
from sqlalchemy_utils.types import UUIDType


class CommunityMetadata(db.Model, RecordMetadataBase):
    """Represent a community."""

    __tablename__ = "communities_metadata"

    slug = db.Column(String(255), unique=True, nullable=True)

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class CommunityFileMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a community."""

    __record_model_cls__ = CommunityMetadata

    __tablename__ = "communities_files"


class CommunityFeatured(db.Model, Timestamp):
    """Featured community entry."""

    __tablename__ = "communities_featured"

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(
        UUIDType, db.ForeignKey(CommunityMetadata.id), nullable=False
    )
    start_date = db.Column(
        db.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
        nullable=False,
        default=datetime.utcnow,
    )
