# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Implements a Redis cache."""
from cachelib import RedisCache
from flask import current_app
from redis import StrictRedis

from invenio_communities.cache.cache import IdentityCache


class IdentityRedisCache(IdentityCache):
    """Redis image cache."""

    def __init__(self, app=None):
        """Initialize the cache."""
        super().__init__(app=app)
        app = app or current_app
        redis_url = app.config["COMMUNITIES_IDENTITIES_CACHE_REDIS_URL"]
        prefix = app.config.get("COMMUNITIES_IDENTITIES_CACHE_REDIS_PREFIX", "identity")
        self.cache = RedisCache(host=StrictRedis.from_url(redis_url), key_prefix=prefix)

    def get(self, key):
        """Return the key value.

        :param key: the object's key
        :return: the stored object
        """
        return self.cache.get(key)

    def set(self, key, value, timeout=None):
        """Cache the object.

        :param key: the object's key
        :param value: the stored object
        :param timeout: the cache timeout in seconds
        """
        timeout = timeout or self.timeout
        self.cache.set(key, value, timeout=timeout)

    def delete(self, key):
        """Delete the specific key."""
        self.cache.delete(key)

    def flush(self):
        """Flush the cache."""
        self.cache.clear()

    def append(self, key, value):
        """Appends a new value to a list.

        :param key: the object's key
        :param value: the stored list
        """
        values_list = self.cache.get(key)
        if values_list:
            if not isinstance(values_list, list):
                raise TypeError(
                    "Value {value} must be a list but was {type}".format(
                        value=values_list, type=type(values_list)
                    )
                )
            if value not in values_list:
                values_list.append(value)
        else:
            values_list = [value]
        self.set(key, values_list)
