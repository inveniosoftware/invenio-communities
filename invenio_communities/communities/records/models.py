# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community database models."""

from __future__ import absolute_import, print_function

from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records import FileRecordModelMixin
from sqlalchemy_utils.types import UUIDType


class CommunityMetadata(db.Model, RecordMetadataBase):
    """Represent a community."""

    __tablename__ = 'communities_metadata'

    # Enables SQLAlchemy-Continuum versioning
    __versioned__ = {}

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class CommunityFileMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a community."""

    __record_model_cls__ = CommunityMetadata

    __tablename__ = 'communities_files'
