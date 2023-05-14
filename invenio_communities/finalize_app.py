# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Finalize app."""

from flask import g
from flask_menu import current_menu
from invenio_i18n import lazy_gettext as _

from .proxies import current_communities


def _can_create_community():
    """Function used to check if a user has permissions to create a community."""
    can_create = current_communities.service.check_permission(g.identity, "create")
    return can_create


def finalize_app(app):
    """Finalize app."""
    register_menus()


def register_menus():
    """Register community menu items."""
    current_menu.submenu("main.communities").register(
        "invenio_communities.communities_frontpage",
        "Communities",
        order=1,
    )
    current_menu.submenu("plus.community").register(
        "invenio_communities.communities_new",
        "New community",
        order=3,
        visible_when=_can_create_community,
    )

    communities = current_menu.submenu("communities")

    communities.submenu("requests").register(
        "invenio_communities.communities_requests",
        text=_("Requests"),
        order=2,
        expected_args=["pid_value"],
        **{"icon": "comments", "permissions": "can_search_requests"}
    )
    communities.submenu("members").register(
        "invenio_communities.members",
        text=_("Members"),
        order=3,
        expected_args=["pid_value"],
        **{"icon": "users", "permissions": "can_read"}
    )

    communities.submenu("settings").register(
        "invenio_communities.communities_settings",
        text=_("Settings"),
        order=4,
        expected_args=["pid_value"],
        **{"icon": "settings", "permissions": "can_update"}
    )
    communities.submenu("curation_policy").register(
        "invenio_communities.communities_curation_policy",
        text=_("Curation policy"),
        order=5,
        expected_args=["pid_value"],
        **{"icon": "balance scale", "permissions": "can_read"}
    )
    communities.submenu("about").register(
        "invenio_communities.communities_about",
        text=_("About"),
        order=6,
        expected_args=["pid_value"],
        **{"icon": "info", "permissions": "can_read"}
    )
