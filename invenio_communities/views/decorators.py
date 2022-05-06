# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
from functools import wraps

from flask import current_app, g

from invenio_communities.proxies import current_communities
from invenio_records_resources.proxies import current_service_registry

def getRoles(action, member_types, community):
    """Get roles allowed for a given action, member type and community"""
    roles = []
    for role in current_app.config['COMMUNITIES_ROLES']:
        if current_service_registry.get("communities").config.permission_policy_cls(
            action,
            community_id=community.to_dict()["uuid"],
            role=role["name"],
            member_types=member_types
        ).allows(g.identity):
            roles.append(role)
    return roles

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


def pass_roles(f):
    """Decorate a view to pass the roles that a user can manage."""
    @wraps(f)
    def view(**kwargs):
        """."""
        roles={}
        community = kwargs['community']
        user = 'user'
        group = 'group'
        roles[user] = getRoles('members_invite', {user}, community)
        roles[group] = getRoles('members_add', {group}, community)
        kwargs['roles'] = roles

        return f(**kwargs)
    return view
