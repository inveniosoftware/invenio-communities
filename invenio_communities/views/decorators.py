# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
from functools import wraps

from flask import g
from invenio_records_resources.services.errors import PermissionDeniedError

from invenio_communities.proxies import current_communities


def service():
    """Get the communities service."""
    return current_communities.service


def pass_community(f):
    """Decorate to retrieve the community record using the community service.
    """
    @wraps(f)
    def view(**kwargs):
        pid_value = kwargs['pid_value']
        community = service().read(
            id_=pid_value, identity=g.identity
        )
        kwargs['community'] = community
        return f(**kwargs)
    return view


def pass_community_logo(f):
    """Decorate a view to pass a community logo using the files service."""
    @wraps(f)
    def view(**kwargs):
        """."""
        try:
            pid_value = kwargs['pid_value']
            files = service().read_logo(
                id_=pid_value, identity=g.identity
            )
            kwargs['logo'] = files
        except FileNotFoundError:
            kwargs['logo'] = None

        return f(**kwargs)
    return view


def pass_community_endpoint(f):
    """Decorate a view to calculate community endpoint."""
    @wraps(f)
    def view(**kwargs):
        """."""
        community = kwargs['community']
        base_endpoint = f'/api/communities/{community.to_dict()["uuid"]}/members'  # TODO: change to community.id (once backend ready)
        if community.has_permissions_to(["members_search"])[
            "can_members_search"
        ]:
            endpoint = base_endpoint
        elif community.has_permissions_to(["members_search_public"])[
            "can_members_search_public"
        ]:
            endpoint = base_endpoint + "/public"
        else:
            raise PermissionDeniedError()
        kwargs['endpoint'] = endpoint
        return f(**kwargs)
    return view
