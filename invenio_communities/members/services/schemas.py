# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Member schema."""

from datetime import timezone
from types import SimpleNamespace

from flask_babelex import lazy_gettext as _
from invenio_users_resources.proxies import (
    current_groups_service,
    current_users_service,
)
from marshmallow import Schema, ValidationError, fields, validate, validates_schema
from marshmallow_utils.fields import SanitizedUnicode, TZDateTime

from .fields import RoleField


#
# Utility schemas
#
class MemberEntitySchema(Schema):
    """Represents a single member entity."""

    type = fields.String(
        required=True, validate=validate.OneOf(["user", "group", "email"])
    )
    id = fields.String(required=True)
    is_current_user = fields.Bool(dump_only=True)


class MembersSchema(Schema):
    """Members Schema."""

    members = fields.List(
        fields.Nested(MemberEntitySchema),
        # max is on purpose to limit the max number of additions/changes/
        # removals per request as they all run in a single transaction and
        # requires resources to hold.
        validate=validate.Length(min=1, max=100),
    )


class RequestSchema(Schema):
    """Request Schema."""

    id = fields.String()
    status = fields.String()
    is_open = fields.Boolean()
    # TODO: expires_at is dumped in the index and thus a string. This is
    # because the relations field doesn't properly load data from the index
    # (it should have converted expires_at into a datetime object).
    expires_at = fields.String()


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
        if "role" not in data and "visible" not in data:
            raise ValidationError(_("Missing fields 'role' and/or 'visible'."))


class DeleteBulkSchema(MembersSchema):
    """Delete bulk schema."""


#
# Schemas used for dumping a single member
#


class PublicDumpSchema(Schema):
    """Public Dump Schema."""

    id = fields.String(required=True)
    member = fields.Method("get_member")

    def get_member(self, obj):
        """Get a member."""
        if obj.user_id:
            return self.get_user_member(obj["user"])
        elif obj.group_id:
            return self.get_group_member(obj["group"])

    def get_user_member(self, user):
        """Get a user member."""
        profile = user.get("profile", {})
        name = profile.get("full_name") or user.get("username") or _("Untitled")
        description = profile.get("affiliations") or ""
        fake_user_obj = SimpleNamespace(id=user["id"])
        avatar = current_users_service.links_item_tpl.expand(fake_user_obj)["avatar"]

        return {
            "type": "user",
            "id": user["id"],
            "name": name,
            "description": description,
            "avatar": avatar,
        }

    def get_group_member(self, group):
        """Get a group member."""
        fake_group_obj = SimpleNamespace(id=group["id"])
        avatar = current_groups_service.links_item_tpl.expand(fake_group_obj)["avatar"]
        return {
            "type": "group",
            "id": group["id"],
            "name": group["id"] or "",
            "avatar": avatar,
        }


class MemberDumpSchema(PublicDumpSchema):
    """Schema for dumping members."""

    role = fields.String()
    visible = fields.Boolean()

    is_current_user = fields.Method("get_current_user")
    permissions = fields.Method("get_permissions")

    created = TZDateTime(timezone=timezone.utc, format="iso")
    updated = TZDateTime(timezone=timezone.utc, format="iso")
    revision_id = fields.Integer()

    def is_self(self, obj):
        """Get permission."""
        if "is_self" not in self.context:
            current_identity = self.context["identity"]
            self.context["is_self"] = (
                obj.user_id is not None
                and current_identity.id is not None
                and str(obj.user_id) == str(current_identity.id)
            )
        return self.context["is_self"]

    def get_current_user(self, obj):
        """Get permission."""
        return self.is_self(obj)

    def get_permissions(self, obj):
        """Get permission."""
        permission_check = self.context["field_permission_check"]

        # Does not take CommunitySelfMember into account because no "member" is
        # passed to the permission check.
        can_update = permission_check(
            "members_update",
            community_id=obj.community_id,
            role=obj.role,
        )
        is_self = self.is_self(obj)

        # The rules below are defined by the update()/delete() methods in the
        # service.
        return {
            "can_leave": is_self,
            "can_delete": can_update and not is_self,
            "can_update_role": can_update and not is_self,
            "can_update_visible": (obj.visible and can_update) or is_self,
        }


class InvitationDumpSchema(MemberDumpSchema):
    """Schema for dumping invitations."""

    request = fields.Nested(RequestSchema)
    permissions = fields.Method("get_permissions")

    def get_permissions(self, obj):
        """Get permission."""
        # Only owners and managers can list invitations, and thus only the
        # request status is necessary to determine if the identity can cancel.
        is_open = obj["request"]["status"] == "submitted"
        permission_check = self.context["field_permission_check"]

        return {
            "can_cancel": is_open,
            "can_update_role": is_open
            and permission_check(
                "members_update",
                community_id=obj.community_id,
                member=obj,
            ),
        }
