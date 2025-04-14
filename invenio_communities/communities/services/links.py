# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utility for rendering URI template links."""

from flask import current_app
from invenio_records_resources.services.base.links import Link, LinksTemplate


def children_allowed(record, _):
    """Determine if children are allowed."""
    try:
        return getattr(record.children, "allow", False)
    except AttributeError:
        # This is needed because a types.SimpleNamespace object can be passed by
        # the entity_resolver when generating the logo which does not have
        # `children` and fails
        return False


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


class CommunityLinks(object):
    """Factory class for Community routes."""

    communities_default_routes = {
        "self": CommunityLink("{+api}/communities/{id}"),
        "self_html": CommunityLink("{+ui}/communities/{slug}"),
        "settings_html": CommunityLink("{+ui}/communities/{slug}/settings"),
        "logo": CommunityLink("{+api}/communities/{id}/logo"),
        "rename": CommunityLink("{+api}/communities/{id}/rename"),
        "members": CommunityLink("{+api}/communities/{id}/members"),
        "public_members": CommunityLink("{+api}/communities/{id}/members/public"),
        "invitations": CommunityLink("{+api}/communities/{id}/invitations"),
        "requests": CommunityLink("{+api}/communities/{id}/requests"),
        "records": CommunityLink("{+api}/communities/{id}/records"),
        "subcommunities": CommunityLink(
            "{+api}/communities/{id}/subcommunities",
            when=children_allowed,
        ),
        "membership_requests": CommunityLink(
            "{+api}/communities/{id}/membership-requests"
        ),
    }

    @classmethod
    def convert_config_routes(cls, custom_routes: dict) -> dict:
        """Convert config routes to the links string template format.

        Only convert routes that have a corresponding default link
        ending in "_html".
        """
        return {
            f"{k}_html": CommunityLink("{+ui}" + v.replace("<pid_value>", "{slug}"))
            for k, v in custom_routes.items()
            if f"{k}_html" in cls.communities_default_routes.keys()
        }

    @classmethod
    def get_item_links(cls, routes: dict = None) -> dict:
        """Get the item links customized from the config routes."""
        routes = cls.communities_default_routes.copy() if not routes else routes
        routes_from_config = current_app.config.get("COMMUNITIES_ROUTES", {})
        routes.update(cls.convert_config_routes(routes_from_config))

        return routes


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
