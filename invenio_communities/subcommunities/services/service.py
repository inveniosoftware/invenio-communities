# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunities service."""

from invenio_i18n import gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services.base import LinksTemplate, Service
from invenio_records_resources.services.records.links import pagination_links
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests.proxies import current_requests_service as requests_service
from invenio_search.engine import dsl
from werkzeug.local import LocalProxy

import invenio_communities.notifications.builders as notifications
from invenio_communities.proxies import current_communities, current_roles

from .errors import ParentChildrenNotAllowed

community_service = LocalProxy(lambda: current_communities.service)


class SubCommunityService(Service):
    """Subcommunities service."""

    @property
    def request_cls(self):
        """Request class."""
        return self.config.request_cls

    @property
    def schema(self):
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def links_item_tpl(self):
        """Item links template."""
        return LinksTemplate(
            self.config.links_item,
            context={
                "permission_policy_cls": self.config.permission_policy_cls,
            },
        )

    @property
    def expandable_fields(self):
        """Get expandable fields."""
        return []

    def _is_owner_of(self, identity, community):
        """Check if the identity provides community ownership."""
        return next(
            (
                x
                for x in identity.provides
                if x.method == "community"
                and x.value == community
                and x.role == current_roles.owner_role.name
            ),
            None,
        )

    def search(self, identity, id_, **kwargs):
        """Return list of subcommunities."""
        subcommunities = community_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must", must=[dsl.Q("term", **{"parent.id": id_})]
            ),
            **kwargs
        )
        self_link = LinksTemplate(
            # https://github.com/inveniosoftware/invenio-communities/issues/1218
            # pagination_links("{+api}/communities/{community_id}/subcommunities{?args*}"),
            pagination_links("{+api}/communities/{community_id}/subcommunities"),
            context={"community_id": id_},
        )
        subcommunities._links_tpl = self_link
        return subcommunities

    @unit_of_work()
    def join(self, identity, id_, data, uow=None):
        """Request to join a subcommunity.

        Permissions are delegated to the communities and requests services. E.g. the
        request service will check if the user has the permission to act on behalf of the
        community.

        This method uses the unit of work pattern, therefore if any permission is
        denied, the transaction will be rolled back.
        """
        parent_community = community_service.record_cls.pid.resolve(id_)

        if not parent_community.children.allow:
            raise ParentChildrenNotAllowed(
                _("Parent community does not accept subcommunities.")
            )

        data_, errors = self.schema.load(
            data,
            context={"identity": identity, "community": parent_community},
            raise_errors=True,
        )

        community = None
        if "community_id" in data_:
            community = community_service.record_cls.pid.resolve(data_["community_id"])
        else:
            community = community_service.create(
                identity, data_["community"], uow=uow
            )._record

        self.require_permission(identity, "request_join", record=community)
        # Sender is the community
        creator = {"community": str(community.id)}

        # Receiver is the parent community
        receiver = {"community": str(id_)}

        # Topic is the community
        topic = {"community": str(community.id)}

        # Create and submit the request
        request_data = {
            "title": _('Inclusion of subcommunity "{community}"').format(
                community=community.metadata["title"]
            )
        }
        request_payload = data.get("payload")
        if request_payload:
            request_data["payload"] = request_payload
        request = requests_service.create(
            identity, request_data, self.request_cls, receiver, creator, topic, uow=uow
        )
        uow.register(
            NotificationOp(
                notifications.SubCommunityCreate.build(
                    identity=identity, request=request._request
                )
            )
        )

        # Accept the request if the user is the owner of both communities
        is_owner_child = self._is_owner_of(identity, str(community.id))

        is_owner_parent = self._is_owner_of(identity, str(id_))
        if is_owner_child and is_owner_parent:
            request = requests_service.execute_action(
                identity, request.id, "accept", uow=uow
            )

        return request

        # TODO if the user is the owner of both communities, accept the request automatically

        # TODO add custom implementation for the result item
        # # We want wrap the request result item in a new one to modify the links
        # return self.result_item(
        #     self,
        #     identity,
        #     request._record,
        #     links_tpl=self.links_item_tpl,
        #     expandable_fields=self.expandable_fields,
        #     expand=True,
        # )
