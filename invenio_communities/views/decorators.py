# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Decorators."""

from functools import wraps

from flask import g

from invenio_communities.proxies import current_communities


def pass_community(f):
    """Fetch the community record."""

    @wraps(f)
    def view(**kwargs):
        pid_value = kwargs["pid_value"]
        community = current_communities.service.read(id_=pid_value, identity=g.identity)
        kwargs["community"] = community
        return f(**kwargs)

    return view
