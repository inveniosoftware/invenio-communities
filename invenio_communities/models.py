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
from invenio_records.models import RecordMetadataBase


class CommunityMetadata(db.Model, RecordMetadataBase):
    """Represent a community."""

    __tablename__ = 'community_metadata'
    __versioned__ = {'versioning': False}
