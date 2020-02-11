# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio communities extension."""

from __future__ import absolute_import, print_function


from . import config


class Communities(object):
    """Invenio extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['communities'] = self

    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        for k in dir(config):
            if k.startswith('COMMUNITIES_'):
                if k == 'COMMUNITIES_REST_ENDPOINTS':
                    # Make sure of registration process.
                    app.config['RECORDS_REST_ENDPOINTS'].update(getattr(
                        config, k))
                app.config.setdefault(k, getattr(config, k))
                if k == 'COMMUNITIES_REST_FACETS':
                    # TODO Might be overriden depending on which package is initialised first
                    app.config['RECORDS_REST_FACETS'].update(
                        getattr(config, k))
        app.config.setdefault(
            'SUPPORT_EMAIL', getattr(config, 'SUPPORT_EMAIL'))
