# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitations Service Config."""

from invenio_records_resources.services import RecordServiceConfig


class InvitationServiceConfig(RecordServiceConfig):
    """Invitation Service Config."""

    # TODO: Add permision
    # permission_policy_cls = PermissionPolicy
