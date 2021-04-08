# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio communities extension."""

from __future__ import absolute_import, print_function

from flask_principal import identity_loaded
from invenio_base.utils import obj_or_import_string
from invenio_indexer.signals import before_record_index
from werkzeug.utils import cached_property

from invenio_communities.communities.resource_config import \
    CommunityResourceConfig
from invenio_communities.communities.service_config import \
    CommunityServiceConfig

from . import config
from .communities import CommunityResource, CommunityService


class InvenioCommunities(object):
    """Invenio extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-communities'] = self

        self.init_services(app)
        self.init_resource(app)

    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        for k in dir(config):
            if k.startswith('COMMUNITIES_'):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Initialize communities service."""
        # Services
        self.communities_service = CommunityService(
            CommunityServiceConfig)

    def init_resource(self, app):
        """Initialize communities resources."""
        # Resources
        self.communities_resource = CommunityResource(
            CommunityResourceConfig,
            self.communities_service,
        )
