# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Decorators."""

from functools import wraps
from warnings import warn

from flask import g, request

from invenio_communities.communities.resources.serializer import (
    UICommunityJSONSerializer,
)
from invenio_communities.proxies import current_communities


def pass_community(serialize):
    """Fetch the community record."""

    def decorator(f):
        @wraps(f)
        def view(**kwargs):
            pid_value = kwargs["pid_value"]
            community = current_communities.service.read(
                id_=pid_value, identity=g.identity
            )
            kwargs["community"] = community
            request.community = community.to_dict()
            if serialize:
                community_ui = UICommunityJSONSerializer().dump_obj(community.to_dict())
                kwargs["community_ui"] = community_ui

            return f(**kwargs)

        return view

    return decorator


def warn_deprecation(deprecated_route, new_route):
    """Decorator to log warnings for deprecated routes."""

    def decorator(f):
        @wraps(f)
        def view(**kwargs):
            warn(
                f"The '{deprecated_route}' route is deprecated and will be removed in future releases. "
                f"Please update to use '{new_route}' instead. If you want to keep using the old endpoint, then you can set up redirection separately.",
                DeprecationWarning,
                stacklevel=2,
            )
            return f(**kwargs)

        return view

    return decorator
