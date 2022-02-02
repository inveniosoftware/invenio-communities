# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio communities extension."""

from flask_principal import identity_loaded
from invenio_records_resources.services import FileService

from invenio_communities.communities import CommunityFileServiceConfig, \
    CommunityResource, CommunityResourceConfig, CommunityService, \
    CommunityServiceConfig
from invenio_communities.invitations import InvitationService, \
    InvitationServiceConfig
from invenio_communities.members import MemberService, \
    MemberServiceConfig

from . import config
from .utils import load_community_needs


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

        if app.config["COMMUNITIES_ENABLED"]:
            self.init_services(app)
            self.init_resource(app)
            self.init_hooks(app)

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
        self.service = CommunityService(
            CommunityServiceConfig,
            files_service=FileService(CommunityFileServiceConfig),
            invitations_service=InvitationService(InvitationServiceConfig()),
            members_service=MemberService(MemberServiceConfig())
        )

    def init_resource(self, app):
        """Initialize communities resources."""
        # Resources
        self.communities_resource = CommunityResource(
            CommunityResourceConfig,
            self.service,
        )

    def init_hooks(self, app):
        """Initialize hooks."""
        @identity_loaded.connect_via(app)
        def on_identity_loaded(_, identity):
            load_community_needs(identity, self.service)
