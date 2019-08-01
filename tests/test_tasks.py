# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

from invenio_records.api import Record

from invenio_communities.models import InclusionRequest


def test_community_delete_task(app, db, communities):
    """Test the community deletion task."""
    (comm1, comm2, comm3) = communities
    communities_key = app.config["COMMUNITIES_RECORD_KEY"]
    rec1 = Record.create({'title': 'Foobar'})
    InclusionRequest.create(community=comm1, record=rec1, notify=False)

    assert InclusionRequest.get(comm1.id, rec1.id)

    comm1.accept_record(rec1)
    assert 'comm1' in rec1[communities_key]

    comm1.delete()
    assert comm1.is_deleted
