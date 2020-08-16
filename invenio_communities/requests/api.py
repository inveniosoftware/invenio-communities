# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Requests API."""

from invenio_records.api import Record as RecordBaseAPI

from .models import Comment as CommentModel
from .models import Request as RequestModel


class RequestBase(RecordBaseAPI):
    """Request API class."""

    model_cls = RequestModel
    STATES = {
        'OPEN': 'Open',
        'CLOSED': 'Closed',
    }
    schema = {
        "type": {
            "type": "string",
            # "enum": [...],
        },
        "state": {
            "type": "string",
            # "enum": ["pending", "closed"],
        },
        "assignees": {"type": "int[]"},
        "created_by": {"type": "int"},
    }

    @property
    def state(self):
        """Get request routing key."""
        return self['state']

    @state.setter
    def state(self, new_state):
        """Set request routing key."""
        try:
            new_value = self.STATES[new_state.upper()]
        except KeyError:
            raise ValueError('This is not a valid state, please select one of'
                             ' following options {}'.format(
                                 self.STATES.keys()))
        return new_value

    @property
    def routing_key(self):
        """Get request routing key."""
        return self.model.routing_key if self.model else None

    @routing_key.setter
    def routing_key(self, new_routing_key):
        """Set request routing key."""
        self.model.routing_key = new_routing_key

    @property
    def comments(self):
        """Request comments."""
        return self.model.comments if self.model else None

    def add_comment(self, user, message):
        """Request comments."""
        return CommentModel.create(self.id, user.id, message)

    def delete(self):
        """Delete the request."""
        self.model.delete(self.model)

    @property
    def is_closed(self):
        """Returns true or false depending on the state of the request."""
        return self.state == 'CLOSED'

