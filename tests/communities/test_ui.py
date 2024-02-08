# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community UI views."""
import pytest
from flask import Blueprint

from invenio_communities.views.communities import render_community_theme_template


@pytest.fixture()
def blueprint():
    """Blueprint for loading templates."""
    # This blueprint picks up the tests/templates/ folder, so that we can
    # render templates from inside this folder.
    return Blueprint("tests", __name__, template_folder="templates")


@pytest.fixture()
def theme_app(instance_path, blueprint, app):
    """Application with template theming."""
    app.config["APP_THEME"] = ["semantic-ui"]
    app.register_blueprint(blueprint)

    yield app


def test_template_loader(theme_app):
    """Test template loader."""

    @theme_app.route("/community_theme")
    def community_theme():
        return render_community_theme_template(
            "invenio_test/frontpage.html", theme={"brand": "horizon", "enabled": True}
        )

    @theme_app.route("/")
    def index():
        return render_community_theme_template("invenio_test/frontpage.html")

    c = theme_app.test_client()
    rv = c.get("/community_theme")
    assert b"TEST HORIZON FRONTPAGE" in rv.data
    rv = c.get("/")
    assert b"DEFAULT COMMUNITY FRONTPAGE" in rv.data
