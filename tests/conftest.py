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


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import tempfile

import pytest
from flask import Flask
from flask_babelex import Babel
from flask_cli import FlaskCLI
from flask_menu import Menu
from invenio_accounts import InvenioAccounts
from invenio_assets import InvenioAssets
from invenio_db import InvenioDB, db
from invenio_indexer import InvenioIndexer
from invenio_search import InvenioSearch
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from invenio_communities import InvenioCommunities


@pytest.fixture()
def app(request):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    app = Flask('testapp', instance_path=instance_path)
    app.config.update(
        TESTING=True,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT="CHANGE_ME_ALSO",
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
    )
    FlaskCLI(app)
    Menu(app)
    Babel(app)
    InvenioDB(app)
    InvenioAccounts(app)
    InvenioAssets(app)
    InvenioSearch(app)
    InvenioIndexer(app)
    InvenioCommunities(app)

    with app.app_context():
        if not database_exists(str(db.engine.url)):
            create_database(str(db.engine.url))
        db.create_all()

    def teardown():
        with app.app_context():
            drop_database(str(db.engine.url))
        shutil.rmtree(instance_path)

    request.addfinalizer(teardown)
    return app
