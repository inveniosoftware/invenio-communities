# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Abstract simple identity cache definition."""

from abc import ABC, abstractmethod

from flask import current_app
from werkzeug.utils import cached_property


class IdentityCache(ABC):
    """Abstract cache layer."""

    def __init__(self, app=None):
        """Initialize the cache."""

    @cached_property
    def timeout(self):
        """Return default timeout from config."""
        return current_app.config["COMMUNITIES_IDENTITIES_CACHE_TIME"]

    @abstractmethod
    def get(self, key):
        """Return the key value.

        :param key: the object's key
        """

    @abstractmethod
    def set(self, key, value, timeout=None):
        """Cache the object.

        :param key: the object's key
        :param value: the stored object
        :param timeout: the cache timeout in seconds
        """

    @abstractmethod
    def delete(self, key):
        """Delete the specific key."""

    @abstractmethod
    def flush(self):
        """Flush the cache."""

    @abstractmethod
    def append(self):
        """Flush the cache."""
