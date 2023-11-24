# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community theme dumper.

Dumper used to remove the theme field on dump of a community from a search body.
"""

from invenio_records.dumpers import SearchDumperExt


class CommunityThemeDumperExt(SearchDumperExt):
    """Dumper to remove community theme field from indexing."""

    def __init__(self, key="theme"):
        """Initialize the dumper."""
        self.key = key

    def dump(self, record, data):
        """Remove theme information from indexing."""
        data.pop("theme", None)
