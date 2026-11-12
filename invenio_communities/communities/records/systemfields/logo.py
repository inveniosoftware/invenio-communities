# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Systemfield for the community logo."""

from invenio_records_resources.records.systemfields.calculated import (
    CalculatedIndexedField,
)


class Logo:
    """Community logo state, with access to the underlying file."""

    def __init__(self, data, record=None, file_key="logo"):
        """Constructor."""
        self._data = data or {}
        self._record = record
        self._file_key = file_key

    @property
    def exists(self):
        """Whether the community has a logo.

        For backwards compatibility while reindexing, old documents have no state,
        so assume a logo exists.
        """
        return self._data.get("exists", True)

    @property
    def checksum(self):
        """Checksum of the logo file."""
        return self._data.get("checksum")

    @property
    def size(self):
        """Size of the logo file in bytes."""
        return self._data.get("size")

    @property
    def file(self):
        """Logo file record, or ``None``."""
        return self._record.files.get(self._file_key)


class LogoField(CalculatedIndexedField):
    """Community logo field, computed from ``record.files`` and indexed.

    ``record.logo = value`` stores or replaces the logo, taking what
    ``record.files[key] = value`` takes. ``record.logo = None`` or ``del record.logo``
    removes it.
    """

    def __init__(self, key="logo", file_key="logo"):
        """Constructor."""
        super().__init__(key=key, use_cache=True, index=True)
        self._file_key = file_key

    def calculate(self, record):
        """State of the logo file."""
        file_record = record.files.get(self._file_key)
        if file_record is None:
            return {"exists": False}
        return {
            "exists": True,
            "checksum": file_record.file.checksum,
            "size": file_record.file.size,
        }

    def post_load(self, record, data, loader=None):
        """Read the state from the search dump, without querying the files."""
        # For backwards compatibility while reindexing, old documents have no state,
        # which ``Logo`` treats as having a logo
        self._set_cache(record, data.pop(self.attr_name, None) or {})

    def __get__(self, record, owner=None):
        """Get the record's logo."""
        if record is None:
            return self
        return Logo(self.obj(record), record, file_key=self._file_key)

    def __set__(self, record, value):
        """Store the logo file, or remove it with ``None``."""
        if value is None:
            self.__delete__(record)
            return
        record.files[self._file_key] = value
        self._set_cache(record, self.calculate(record))

    def __delete__(self, record):
        """Remove the logo file."""
        file_record = record.files.pop(self._file_key, None)
        if file_record is not None:
            file_record.delete(force=True)
        self._set_cache(record, {"exists": False})
