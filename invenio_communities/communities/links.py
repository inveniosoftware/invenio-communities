# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Flask-Resources is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utility for rendering URI template links."""

from invenio_records_resources.services.base import Link


class CommunityLink(Link):
    """Short cut for writing record links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update({
            "id": record.pid.pid_value
        })


def pagination_links(tpl):
    """Create pagination links (prev/selv/next) from the same template."""
    return {
        "prev": Link(
            tpl,
            when=lambda pagination, ctx: pagination.has_prev,
            vars=lambda pagination, vars: vars["args"].update({
                "page": pagination.prev_page.page
            })
        ),
        "self": Link(tpl),
        "next": Link(
            tpl,
            when=lambda pagination, ctx: pagination.has_next,
            vars=lambda pagination, vars: vars["args"].update({
                "page": pagination.next_page.page
            })
        ),
    }
