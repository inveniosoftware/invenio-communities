# SPDX-FileCopyrightText: 2026 Northwestern University.
# SPDX-License-Identifier: MIT

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

        Works without implementation for now.
        """
        pass
