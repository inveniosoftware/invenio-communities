# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""DataCite PID provider."""

from __future__ import absolute_import

from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.base import BaseProvider


class CommunitiesIdProvider(BaseProvider):
    """Community identifier provider.

    This is the recommended community id provider.

    It uses the value of the 'id' present in our data to generate the
    identifier.
    """

    pid_type = 'comid'
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name."""

    object_type = 'rec'
    """Type of object."""

    default_status = PIDStatus.REGISTERED
    """Community IDs with an object are by default registered.

    Default: :attr:`invenio_pidstore.models.PIDStatus.REGISTERED`
    """

    @classmethod
    def create(cls, record, **kwargs):
        """Create a new commuinity identifier.

        For more information about parameters,
        see :meth:`invenio_pidstore.providers.base.BaseProvider.create`.

        :param record: The community record.
        :param kwargs: dict to hold generated pid_value and status. See
            :meth:`invenio_pidstore.providers.base.BaseProvider.create` extra
            parameters.
        :returns: A :class:`CommunitiesIdProvider` instance.
        """
        kwargs['pid_value'] = record['id']
        kwargs['status'] = cls.default_status
        kwargs['object_type'] = cls.object_type
        kwargs['object_uuid'] = record.model.id
        return super(CommunitiesIdProvider, cls).create(**kwargs)

    @classmethod
    def update(cls, pid, new_value):
        """`Update the value of the Community identifier`.

        :param pid: Persistent Identifier type.
        :param new_value: The new string value.

        :returns: A :class:`CommunitiesIdProvider` instance.
        """
        try:
            existing_pid = cls.get(new_value).pid
        except PIDDoesNotExistError:
            pass
        else:
            raise PIDAlreadyExists(
                existing_pid.pid_type,
                existing_pid.pid_value
            )
        pid.pid_value = new_value
        return cls(pid)
