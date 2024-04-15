# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2023-2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio communities extension."""

from flask import g
from flask_menu import current_menu
from flask_principal import identity_loaded
from invenio_accounts.signals import datastore_post_commit
from invenio_base.utils import load_or_import_from_config
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import FileService

from invenio_communities.communities import (
    CommunityFileServiceConfig,
    CommunityResource,
    CommunityResourceConfig,
    CommunityService,
    CommunityServiceConfig,
)
from invenio_communities.members import (
    MemberResource,
    MemberResourceConfig,
    MemberService,
    MemberServiceConfig,
)

from . import config
from .cache.cache import IdentityCache
from .roles import RoleRegistry
from .utils import load_community_needs, on_datastore_post_commit
from .views.ui import (
    _has_about_page_content,
    _has_curation_policy_page_content,
    _show_create_community_link,
)


class InvenioCommunities(object):
    """Invenio extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["invenio-communities"] = self

        self.init_services(app)
        self.init_resource(app)
        self.init_hooks(app)
        self.init_cache(app)

    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        for k in dir(config):
            if k.startswith("COMMUNITIES_"):
                app.config.setdefault(k, getattr(config, k))

        self.roles_registry = RoleRegistry(app.config["COMMUNITIES_ROLES"])

    def init_services(self, app):
        """Initialize communities service."""
        # Services
        self.service = CommunityService(
            CommunityServiceConfig.build(app),
            files_service=FileService(CommunityFileServiceConfig.build(app)),
            members_service=MemberService(MemberServiceConfig.build(app)),
        )

    def init_resource(self, app):
        """Initialize communities resources."""
        # Resources
        self.communities_resource = CommunityResource(
            CommunityResourceConfig.build(app),
            self.service,
        )
        self.members_resource = MemberResource(
            MemberResourceConfig,
            self.service.members,
        )

    def init_hooks(self, app):
        """Initialize hooks."""
        datastore_post_commit.connect(on_datastore_post_commit)

        @identity_loaded.connect_via(app)
        def on_identity_loaded(_, identity):
            load_community_needs(identity)

    def cache_handler(self, app):
        """Return the cache handler."""
        handler_func = load_or_import_from_config(
            "COMMUNITIES_IDENTITIES_CACHE_HANDLER", app
        )
        handler = handler_func(app)
        assert isinstance(handler, IdentityCache)
        return handler

    def init_cache(self, app):
        """Initialize cache."""
        self.cache = self.cache_handler(app)


def api_finalize_app(app):
    """Finalize app."""
    init(app)


def finalize_app(app):
    """Finalize app."""
    init(app)
    register_menus(app)


def register_menus(app):
    """Register community menu items."""
    current_menu.submenu("main.communities").register(
        endpoint="invenio_communities.communities_frontpage",
        text=_("Communities"),
        order=1,
    )
    current_menu.submenu("plus.community").register(
        endpoint="invenio_communities.communities_new",
        text=_("New community"),
        order=2,
        visible_when=_show_create_community_link,
    )

    communities = current_menu.submenu("communities")

    communities.submenu("requests").register(
        endpoint="invenio_communities.communities_requests",
        text=_("Requests"),
        order=20,
        expected_args=["pid_value"],
        **{"icon": "inbox", "permissions": "can_search_requests"}
    )
    communities.submenu("members").register(
        endpoint="invenio_communities.members",
        text=_("Members"),
        order=30,
        expected_args=["pid_value"],
        **{"icon": "users", "permissions": "can_members_search_public"}
    )

    communities.submenu("settings").register(
        endpoint="invenio_communities.communities_settings",
        text=_("Settings"),
        order=40,
        expected_args=["pid_value"],
        **{"icon": "settings", "permissions": "can_update"}
    )

    communities.submenu("curation_policy").register(
        endpoint="invenio_communities.communities_curation_policy",
        text=_("Curation policy"),
        order=50,
        visible_when=_has_curation_policy_page_content,
        expected_args=["pid_value"],
        **{"icon": "balance scale", "permissions": "can_read"}
    )
    communities.submenu("about").register(
        endpoint="invenio_communities.communities_about",
        text=_("About"),
        order=60,
        visible_when=_has_about_page_content,
        expected_args=["pid_value"],
        **{"icon": "info", "permissions": "can_read"}
    )


def init(app):
    """Init app."""
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    rr_ext = app.extensions["invenio-records-resources"]
    idx_ext = app.extensions["invenio-indexer"]
    ext = app.extensions["invenio-communities"]

    # services
    rr_ext.registry.register(ext.service, service_id="communities")
    rr_ext.registry.register(ext.service.members, service_id="members")

    # indexers
    idx_ext.registry.register(ext.service.indexer, indexer_id="communities")
    idx_ext.registry.register(ext.service.members.indexer, indexer_id="members")
    idx_ext.registry.register(
        ext.service.members.archive_indexer, indexer_id="archived-invitations"
    )

    # change notification handlers
    rr_ext.notification_registry.register("users", ext.service.on_relation_update)
