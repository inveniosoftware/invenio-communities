# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Links generation for the members service."""

from invenio_records_resources.services.base.links import Link, LinksTemplate
from invenio_requests.customizations import RequestActions
from invenio_requests.proxies import (
    current_request_type_registry,
    current_requests_service,
)
from invenio_requests.resolvers.registry import ResolverRegistry
from uritemplate import URITemplate


class LinksForActionsOfMember:
    """Intermediary template of links.

    It responds to the same interface as a `Link`, but is used to dynamically generate
    the dict of different possible action links of a Member.

    This is part of allowing us to save on extra attributes on the config and condensing
    link generation where it belongs to a narrow interface with deep logic.
    """

    def __init__(self, links_for_actions):
        """Constructor.

        :param links_for_actions: list of Link-like
        """
        self._links_for_actions = links_for_actions

    def expand(self, obj, context):
        """Expand all the action link templates.

        :param obj: api.Member
        :param context: dict of contextual values

        :return: dict of links
        """
        links = {}
        for link in self._links_for_actions:
            if link.should_render(obj, context):
                link.expand(obj, context, into=links)
        return links

    def should_render(self, obj, context):
        """Conforms to `Link` interface but always renders.

        Consequence: will always render the key even if no action links should render
        i.e. if empty dict. This is probably simpler for frontend too.
        """
        return True


class RequestLike:
    """A Request like object for interface purposes."""

    def __init__(self, obj, context):
        """Constructor.

        May raise IndexError (and that's Ok - should be handled).

        :param obj: api.Member
        :param context: dict of context values
        """
        self.id = obj.request_id
        request_relation = obj["request"]
        self.type = current_request_type_registry.lookup(request_relation["type"])
        self.status = request_relation["status"]
        self.created_by = self._get_created_by(obj)
        self.receiver = self._get_receiver(obj)

    def _get_created_by(self, obj):
        """Get the created_by field's proxy.

        Assigns a Proxy to `created_by` based on the type of request
        associated with obj.

        Warning: constructor method: not full self yet.

        :param obj: api.Member
        """
        # This assertion is to alert us developers if the associated
        # ref_types certainty of only 1 type changes. If it does, we need to rethink
        # things.
        assert 1 == len(self.type.allowed_creator_ref_types)

        creator_ref_type = self.type.allowed_creator_ref_types[0]
        return self._get_proxy_by_ref_type(creator_ref_type, obj)

    def _get_receiver(self, obj):
        """Set the receiver field.

        Assigns a Proxy to `receiver` based on the type of request associated with obj.

        Warning: constructor method: not full self yet.

        :param obj: api.Member
        """
        # This assertion is to alert us developers if the associated
        # ref_types certainty of only 1 type changes. If it does, we need to rethink
        # things.
        assert 1 == len(self.type.allowed_receiver_ref_types)

        receiver_ref_type = self.type.allowed_receiver_ref_types[0]
        return self._get_proxy_by_ref_type(receiver_ref_type, obj)

    def _get_proxy_by_ref_type(self, ref_type, obj):
        """Returns proxy for given ref type.

        :param ref_type: string key of reference type
        :param obj: api.Member
        """
        if ref_type == "community":
            # This *creates* an entity proxy contrary to the name
            return ResolverRegistry.resolve_entity_proxy(
                {"community": obj.community_id}
            )
        elif ref_type == "user":
            # This *creates* an entity proxy contrary to the name
            return ResolverRegistry.resolve_entity_proxy({"user": obj.user_id})
        else:
            # again mostly for developers to be alerted
            raise Exception("ref_type is unknown!")


class LinksForRequestActionsOfMember:
    """Links specifically for the request related to the Member."""

    def __init__(self, uritemplate):
        """Constructor."""
        # Only accepting the uritemplate as arg for "consistency" with other Link-likes
        # so that URLs can be perused on skimming a service's config.
        self._uritemplate = uritemplate

    def should_render(self, obj, context):
        """Render based on if there is an associated request at all.

        :param obj: api.Member
        :param context: dict of context values
        """
        try:
            RequestLike(obj, context)
            return True
        except KeyError:
            return False

    def expand(self, obj, context, into):
        """Expand all the member's request's action links templates.

        :param obj: api.Member
        :param context: dict of context values
        :param into: dict of resulting links
        """
        # Know that we can get a RequestLike without issue at this point since
        # should_render has returned True.
        request_like = RequestLike(obj, context)

        for action in request_like.type.available_actions:
            link = LinkForRequestAction(self._uritemplate, action)
            if link.should_render(request_like, context):
                into[action] = link.expand(request_like, context)


class LinkForRequestAction(Link):
    """Link for the action of a request."""

    def __init__(self, uritemplate, action):
        """Constructor."""
        self._uritemplate = URITemplate(uritemplate)
        self.action = action

    def _vars_func(self, request, vars):
        """Inject the passed vars (context) with items specific to this Link.

        `vars` has been copied at this point and therefore can be
        modified in-place.

        :param request: RequestLike
        :param vars: dict of contextual values
        """
        vars.update({"action": self.action, "request_id": request.id})

    def should_render(self, request, context):
        """Determine if the link should render."""
        action_for_execute = self.action
        action_for_permission = f"action_{action_for_execute}"
        identity = context.get("identity")
        permission = current_requests_service.permission_policy(
            action_for_permission,
            request=request,
        )
        # fmt: off
        return (
            RequestActions.can_execute(request, action_for_execute)
            and permission.allows(identity)
        )
        # fmt: on
