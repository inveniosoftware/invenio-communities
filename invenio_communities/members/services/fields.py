# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-FileCopyrightText: 2023 Graz University of Technology.
# SPDX-FileCopyrightText: 2024 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""Marshmallow fields."""

from invenio_i18n import lazy_gettext as _
from marshmallow import fields

from ...proxies import current_roles
from ...roles import Role


class RoleField(fields.Str):
    """Role field that serializes/deserializes/validates Role objects."""

    default_error_messages = {"invalid_role": _("Invalid role.")}

    def __init__(self, *args, **kwargs):
        """Field constructor.

        :param roles: A role registry. Defaults to the current roles.
        """
        self.roles = kwargs.pop("roles", current_roles)
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if value not in current_roles:
            raise self.make_error("invalid_role")
        return self.roles[value]

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        elif isinstance(value, Role):
            return value.name
        elif isinstance(value, str):
            if value in current_roles:
                return value
        raise RuntimeError(_("Not a valid role to serialize."))
