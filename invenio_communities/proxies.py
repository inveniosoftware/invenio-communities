# SPDX-FileCopyrightText: 2016-2022 CERN.
# SPDX-License-Identifier: MIT

"""Proxy definitions."""

from flask import current_app
from werkzeug.local import LocalProxy

current_communities = LocalProxy(lambda: current_app.extensions["invenio-communities"])
"""Proxy to the extension."""


current_roles = LocalProxy(
    lambda: current_app.extensions["invenio-communities"].roles_registry
)
"""Proxy to the roles."""

current_identities_cache = LocalProxy(
    lambda: current_app.extensions["invenio-communities"].cache
)
"""Proxy to the cache."""
