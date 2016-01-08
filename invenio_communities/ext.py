# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module that adds support for communities."""

from __future__ import absolute_import, print_function

from invenio_indexer import signals

from . import config
from .cli import communities as cmd
from .receivers import inject_provisional_community
from .views import blueprint


class InvenioCommunities(object):
    """Invenio-Communities extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.cli.add_command(cmd)
        app.register_blueprint(blueprint)
        app.extensions['invenio-communities'] = self
        # Register the jinja do extension
        app.jinja_env.add_extension('jinja2.ext.do')
        # Register the provisional community signal receiver
        signals.before_record_index.connect(inject_provisional_community)

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            "COMMUNITIES_BASE_TEMPLATE",
            app.config.get("BASE_TEMPLATE",
                           "invenio_communities/base.html"))

        # Set default configuration
        for k in dir(config):
            if k.startswith("COMMUNITIES_"):
                app.config.setdefault(k, getattr(config, k))
