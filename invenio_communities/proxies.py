# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Proxy definitions."""

from flask import current_app
from werkzeug.local import LocalProxy

current_communities = LocalProxy(lambda: current_app.extensions["invenio-communities"])
"""Proxy to the extension."""


current_roles = LocalProxy(
    lambda: current_app.extensions["invenio-communities"].roles_registry
)
"""Proxy to the extension."""
