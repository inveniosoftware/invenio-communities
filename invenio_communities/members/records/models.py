# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Member Model."""

import uuid

from invenio_db import db
from invenio_accounts.models import User
from invenio_records.models import RecordMetadataBase
from sqlalchemy_utils.types import UUIDType

from ...communities.records.models import CommunityMetadata


class MemberModel(db.Model, RecordMetadataBase):
    """Member model."""

    __tablename__ = "communities_members"

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    community_id = db.Column(
        UUIDType,
        db.ForeignKey(CommunityMetadata.id, ondelete="CASCADE"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="CASCADE"),
        nullable=True
    )

    role = db.Column(db.String(50), nullable=False)

    # TODO: add group + visibility
