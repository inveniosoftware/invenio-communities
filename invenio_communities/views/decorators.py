# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from functools import wraps

from flask import g

from invenio_communities.proxies import current_communities


def service():
    """Get the communities service."""
    return current_communities.service


def pass_community(f):
    """Decorate to retrieve the community record using the community service.
    """
    @wraps(f)
    def view(**kwargs):
        pid_value = kwargs.get('pid_value')
        community = service().read(
            id_=pid_value, identity=g.identity
        )
        kwargs['community'] = community
        return f(**kwargs)
    return view
