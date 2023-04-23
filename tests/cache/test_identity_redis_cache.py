# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Image Redis Cache Tests."""

import time

from invenio_communities.proxies import current_identities_cache


def test_cache_deletion(app):
    """Test cache delete function."""
    current_identities_cache.set("foo", "bar")
    assert current_identities_cache.get("foo") == "bar"
    current_identities_cache.delete("foo")
    assert current_identities_cache.get("foo") is None


def test_cache_flush(app):
    """Test cache flush function."""
    current_identities_cache.set("foo_1", "bar")
    current_identities_cache.set("foo_2", "bar")
    current_identities_cache.set("foo_3", "bar")
    for i in [1, 2, 3]:
        assert current_identities_cache.get("foo_{0}".format(i)) == "bar"
    current_identities_cache.flush()
    for i in [1, 2, 3]:
        assert current_identities_cache.get("foo_{0}".format(i)) is None


def test_default_prefix_for_redis(app):
    """Test default redis prefix"""
    # Test default prefix for redis keys (when nothing set in config)
    assert current_identities_cache.cache.key_prefix == "identity"


def test_timeout_config(app):
    """Test default timeout config."""
    current_identities_cache.set("foo_1", "bar")
    time.sleep(3)
    assert current_identities_cache.get("foo_1") is None
