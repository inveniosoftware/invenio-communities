# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Mock module."""

from flask import Blueprint


def create_invenio_app_rdm_communities_blueprint(app):
    """Create fake invenio_app_rdm_communities Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_communities",
        __name__,
    )

    def communities_home(pid_value, community, community_ui):
        return "<communities home>"

    # Requests URL rules
    blueprint.add_url_rule("/communities/<pid_value>", view_func=communities_home)

    return blueprint


def create_community_records_blueprint(app):
    """Create fake invenio-records Blueprint akin to invenio-rdm-records'."""
    blueprint = Blueprint(
        "community-records",
        __name__,
    )

    def search():
        return "<search>"

    blueprint.add_url_rule("/communities/<pid_value>/records", view_func=search)

    return blueprint
