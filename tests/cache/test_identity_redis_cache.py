# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Image Redis Cache Tests."""

import time
from uuid import uuid4

import pytest
from flask import Flask
from redis import StrictRedis

from invenio_communities.cache.redis import IdentityRedisCache
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


@pytest.mark.parametrize("key_count", [0, 500, 1203])
def test_cache_flush_preserves_other_prefixes(app_config, key_count):
    """Flush full batches and remainders without removing unrelated keys."""
    app = Flask(__name__)
    prefix = f"test-identities-{uuid4().hex}:"
    redis_url = app_config["COMMUNITIES_IDENTITIES_CACHE_REDIS_URL"]
    app.config.update(
        COMMUNITIES_IDENTITIES_CACHE_REDIS_URL=redis_url,
        COMMUNITIES_IDENTITIES_CACHE_REDIS_PREFIX=prefix,
    )
    cache = IdentityRedisCache(app)
    client = StrictRedis.from_url(redis_url)
    matching_keys = [f"{prefix}{i}" for i in range(key_count)]
    outside_keys = [prefix[:-1], f"other:{prefix}key"]
    try:
        client.mset({key: "keep" for key in outside_keys})
        if matching_keys:
            client.mset({key: "remove" for key in matching_keys})
            assert client.mget(matching_keys) == [b"remove"] * key_count

        cache.flush()

        assert list(client.scan_iter(match=f"{prefix}*")) == []
        assert client.mget(outside_keys) == [b"keep", b"keep"]
    finally:
        client.unlink(*matching_keys, *outside_keys)
        client.close()
        cache.redis.close()


def test_default_prefix_for_redis(app):
    """Test default redis prefix"""
    # Test default prefix for redis keys (when nothing set in config)
    assert current_identities_cache.cache.key_prefix == "identity"


def test_timeout_config(app):
    """Test default timeout config."""
    current_identities_cache.set("foo_1", "bar")
    time.sleep(3)
    assert current_identities_cache.get("foo_1") is None
