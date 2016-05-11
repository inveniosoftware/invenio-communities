Fork from invenio-communities to add permissions to communities. This is a
temporary fork, and it should be removed when team management has been added
to the original module from invenio (around end of November 2016)

To update to this fork from the invenio repository, simply follow these
steps (instructions taken from https://gist.github.com/jagregory/710671):

In your local, rename your origin remote to upstream

    git remote rename origin upstream

Add a new origin and use it by default

    git remote add origin git@github.com:tind/invenio-communities.git

    git branch --set-upstream-to origin/master

Fetch & push

    git fetch origin
    git push origin


..
    This file is part of Invenio.
    Copyright (C) 2015, 2016 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

=====================
 Invenio-Communities
=====================

.. image:: https://img.shields.io/travis/inveniosoftware/invenio-communities.svg
        :target: https://travis-ci.org/inveniosoftware/invenio-communities

.. image:: https://img.shields.io/coveralls/inveniosoftware/invenio-communities.svg
        :target: https://coveralls.io/r/inveniosoftware/invenio-communities

.. image:: https://img.shields.io/github/tag/inveniosoftware/invenio-communities.svg
        :target: https://github.com/inveniosoftware/invenio-communities/releases

.. image:: https://img.shields.io/pypi/dm/invenio-communities.svg
        :target: https://pypi.python.org/pypi/invenio-communities

.. image:: https://img.shields.io/github/license/inveniosoftware/invenio-communities.svg
        :target: https://github.com/inveniosoftware/invenio-communities/blob/master/LICENSE


Invenio module that adds support for communities.

*This is an experimental developer preview release.*

* Free software: GPLv2 license
* Documentation: https://pythonhosted.org/invenio-communities/
