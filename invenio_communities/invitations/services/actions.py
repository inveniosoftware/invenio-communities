# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitations Actions."""

from invenio_requests.customizations import RequestAction

from invenio_communities.proxies import current_communities


class AcceptAction(RequestAction):
    """Accept action."""

    status_from = ['open']
    status_to = 'accepted'

    def can_execute(self, identity):
        """Check if the accept action can be executed."""
        # TODO
        return True

    def execute(self, identity, uow):
        """Accept entity into community."""
        # community = self.request.topic.resolve()
        # entity = self.request.receiver.resolve()

        member_data = {
            **self.request.receiver.reference_dict,
            **self.request.topic.reference_dict,
            # TODO: add role
        }

        current_communities.service.members.create(
            identity,
            data=member_data,
            uow=uow
        )

        super().execute(identity, uow)
