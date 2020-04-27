# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Indexer for communities."""

from invenio_indexer.api import RecordIndexer

from .api import Community


class CommunityIndexer(RecordIndexer):
    """Community indexer."""

    record_cls = Community
