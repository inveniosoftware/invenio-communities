# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utility for rendering URI template links."""

from invenio_records_resources.services.base.links import Link, LinksTemplate


class CommunityLinksTemplate(LinksTemplate):
    """Templates for generating links for a community object."""

    def __init__(self, links, action_link, available_actions, context=None):
        """Constructor."""
        super().__init__(links, context=context)
        self._action_link = action_link
        self._available_actions = available_actions

    def expand(self, identity, community):
        """Expand all the link templates."""
        links = {}

        # expand links for all available actions on the request
        link = self._action_link
        for action in self._available_actions:
            ctx = self.context.copy()
            ctx["action_name"] = action["action_name"]
            ctx["action"] = action["action_permission"]
            ctx["identity"] = identity
            if link.should_render(community, ctx):
                links[action["action_name"]] = link.expand(community, ctx)

        # expand the other configured links
        ctx = self.context.copy()
        ctx["identity"] = identity
        for key, link in self._links.items():
            if link.should_render(community, ctx):
                links[key] = link.expand(community, ctx)

        return links


class CommunityLink(Link):
    """Link variables setter for Community Members links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update(
            {
                "id": record.id,
                "slug": record.slug,
            }
        )
