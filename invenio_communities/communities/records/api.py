# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from __future__ import absolute_import, print_function

from invenio_records.systemfields import ConstantField, ModelField
from invenio_records_resources.records.api import FileRecord, Record
from invenio_records_resources.records.systemfields import FilesField, \
    IndexField, PIDField
from werkzeug.local import LocalProxy

from . import models
from .providers import CommunitiesIdProvider
from .systemfields.access import CommunityAccessField


class CommunityFile(FileRecord):
    """Community file API."""

    model_cls = models.CommunityFileMetadata
    record_cls = LocalProxy(lambda: Community)


class Community(Record):
    """Community API."""

    pid = PIDField('id', provider=CommunitiesIdProvider, create=False)
    schema = ConstantField(
        '$schema', 'local://communities/communities-v1.0.0.json')

    model_cls = models.CommunityMetadata

    index = IndexField(
        "communities-communities-v1.0.0",
        search_alias="communities"
    )

    access = CommunityAccessField()

    bucket_id = ModelField(dump=False)
    bucket = ModelField(dump=False)
    files = FilesField(
        store=False,
        file_cls=CommunityFile,
        # Don't delete, we'll manage in the service
        delete=False,
    )
