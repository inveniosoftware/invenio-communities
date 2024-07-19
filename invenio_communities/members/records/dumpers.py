# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Secondary storage (ES/OS) dumpers."""

from invenio_records.dictutils import dict_lookup, dict_set
from invenio_records.dumpers.search import SearchDumperExt


class RequestTypeDumperExt(SearchDumperExt):
    """Dumper for the relations.request.type field."""

    def __init__(self):
        """Initialize the dumper."""
        self.key = "relations.request.type"

    def dump(self, record, data):
        """Dump relations."""
        try:  # In case no associated request type
            request_type = dict_lookup(record, "request.type")
            # Serialize back RequestType to its identifier only
            dict_set(data, "request.type", request_type.type_id)
        except KeyError:
            return

    def load(self, data, record_cls):
        """Load relations.request.type.

        TODO: Works without it for now. Potentially revisit?
        """
        pass
