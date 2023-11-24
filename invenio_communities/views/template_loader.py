# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community theme template loader."""

from flask import current_app
from flask.templating import DispatchingJinjaLoader
from invenio_app.helpers import ThemeJinjaLoader
from jinja2 import ChoiceLoader
from werkzeug.utils import cached_property


class CommunityThemeJinjaLoader(ThemeJinjaLoader):
    """Community theme choice template loader.

    This loader acts as a wrapper for any type of Jinja loader. Before doing a
    template lookup, the loader sequentially applies prefixes to the template
    name, until a template source is found.

    The prefixes are defined via the ``APP_THEME`` configuration variable. This loader
    ensures that the `<brand>` theme takes precedence in the theme lookup.
    """

    def __init__(self, app, loader, brand):
        """Initialize loader.

        :param brand: community brand to be looked up first.
        """
        self.brand = brand
        super().__init__(app, loader)

    @cached_property
    def prefixes(self):
        """Return the active prefixes to be used for template lookup.

        Ensure `community.theme.brand` takes precedence in the list.
        """
        theme = self.app.config.get("APP_THEME", [])
        if isinstance(theme, str):
            # fe. semantic-ui/themes/horizon
            theme = f"themes/{self.brand}"
            theme = [theme]
        elif isinstance(theme, list):
            theme = [f"themes/{self.brand}" for item in theme]
        return theme


class CommunityThemeChoiceJinjaLoader(ChoiceLoader):
    """Community theme choice template loader.

    This loader acts as a wrapper for any type of Jinja ChoiceLoader. Dictates an order
    of theme loaders in the following order:
    - Community theme <brand>
    - Community theme default
    - Default `app.jinja_env.loader`
    """

    def __init__(self, brand):
        """Initialize loader.

        :param brand: community brand to be load .
        """
        self.app = current_app._get_current_object()

        community_theme_loader = CommunityThemeJinjaLoader(
            self.app, DispatchingJinjaLoader(self.app), brand
        )
        default_loader = CommunityThemeJinjaLoader(
            self.app, DispatchingJinjaLoader(self.app), "default"
        )
        super().__init__(
            loaders=[community_theme_loader, default_loader, self.app.jinja_env.loader]
        )
