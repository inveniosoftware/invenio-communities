# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Member schema."""

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, pre_dump, validate, \
    validates_schema
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.fields import TZDateTime
from datetime import timezone

from .fields import RoleField

#
# Utility schemas
#
class MemberEntitySchema(Schema):
    """Represents a single member entity."""

    type = fields.String(
        required=True,
        validate=validate.OneOf(['user', 'group', 'email'])
    )
    id = fields.String(required=True)
    is_current_user = fields.Bool(dump_only=True)


class MembersSchema(Schema):
    members = fields.List(
        fields.Nested(MemberEntitySchema),
        # max is on purpose to limit the max number of additions/changes/
        # removals per request as they all run in a single transaction and
        # requires resources to hold.
        validate=validate.Length(min=1, max=100)
    )


#
# Schemas used for validation
#
class AddBulkSchema(MembersSchema, Schema):
    """Schema used for adding members."""

    role = RoleField(required=True)
    visible = fields.Boolean()


class InviteBulkSchema(AddBulkSchema):
    """Schema used for inviting members."""
    message = SanitizedUnicode()


class UpdateBulkSchema(MembersSchema, Schema):
    """Schema used for updating members."""

    role = RoleField()
    visible = fields.Boolean()

    @validates_schema
    def validate_schema(self, data, **kwargs):
        """Validates that role and/or visible is set."""
        if 'role' not in data and 'visible' not in data:
            raise ValidationError(_("Missing fields 'role' and/or 'visible'"))


class DeleteBulkSchema(MembersSchema):
    """Delete bulk schema."""


#
# Schemas used for dumping a single member
#

class PublicDumpSchema(Schema):
    id = fields.String(required=True)
    member = fields.Method('get_member')

    def get_member(self, obj):
        if obj.user_id:
            return {
                "type": "user",
                "id": str(obj.user_id),
                # TODO: fix all below once indexing is fixed
                # TODO: what about email visibility and public visibility
                "name": f"{obj.user_id}-user-name",
                "description": f"{obj.user_id}-user-description",
                "links": {
                    "avatar": "..."
                }
            }
        elif obj.group_id:
            return {
                "type": "group",
                # TODO: fix me, should be group name
                "id": str(obj.group_id),
                # TODO: fix all below once indexing is fixed
                "name": f"{obj.user_id}-group-name",
                "description": f"{obj.user_id}-group-description",
                "links": {
                    "avatar": "..."
                }
            }


class MemberDumpSchema(PublicDumpSchema):
    role = fields.String()
    visible = fields.Boolean()

    is_current_user = fields.Method('get_current_user')
    permissions = fields.Method('get_permissions')

    created = TZDateTime(timezone=timezone.utc, format='iso')
    updated = TZDateTime(timezone=timezone.utc, format='iso')
    revision_id = fields.Integer()

    def is_self(self, obj):
        if 'is_self' not in self.context:
            current_identity = self.context['identity']
            self.context['is_self'] = (
                obj.user_id is not None and
                current_identity.id is not None and
                str(obj.user_id) == str(current_identity.id)
            )
        return self.context['is_self']

    def get_current_user(self, obj):
        return self.is_self(obj)

    def get_permissions(self, obj):
        return {
            # TODO: is_self and not the last owner
            'can_leave': self.is_self(obj),
            'can_delete': False,
            'can_update_role': False,
            # owners/managers, prior value of visibility, self, prior
            'can_update_visible': self.is_self(obj),
        }
