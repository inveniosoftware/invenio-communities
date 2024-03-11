# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022-2023 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Components."""

from flask import current_app
from invenio_access.permissions import system_identity, system_process
from invenio_db import db
from invenio_i18n import lazy_gettext as _
from invenio_oaiserver.models import OAISet
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records_resources.services.records.components import (
    MetadataComponent,
    RelationsComponent,
    ServiceComponent,
)
from marshmallow.exceptions import ValidationError

from ...proxies import current_roles
from ...utils import on_user_membership_change
from ..records.systemfields.access import VisibilityEnum
from ..records.systemfields.deletion_status import CommunityDeletionStatusEnum


class PIDComponent(ServiceComponent):
    """Service component for Community PIDs."""

    def set_slug(self, record, slug):
        """Set slug."""
        error = ValidationError(
            _("A community with this identifier already exists."), field_name="slug"
        )
        try:
            self.service.record_cls.pid.resolve(slug)
            raise error
        except PIDDeletedError:
            raise error
        except PIDDoesNotExistError:
            record.slug = slug

    def create(self, identity, record=None, data=None, **kwargs):
        """Create a Community PID from its metadata."""
        self.set_slug(record, data["slug"])

    def update(self, identity, record=None, data=None, **kwargs):
        """Rename the Community PIDs value."""
        if "slug" in data and record.slug != data["slug"]:
            raise ValidationError(
                _("The ID should be modified through the renaming URL instead."),
                field_name="slug",
            )

    def rename(self, identity, record=None, data=None, **kwargs):
        """Rename the Community PIDs value."""
        if record.slug == data["slug"]:
            raise ValidationError(
                _("A new ID value is required for the renaming."),
                field_name="slug",
            )
        self.set_slug(record, data["slug"])


class CommunityAccessComponent(ServiceComponent):
    """Service component for access integration."""

    def _populate_access_and_validate(self, identity, data, record, **kwargs):
        """Populate and validate the community's access field."""
        is_modifying_access = record is not None and "access" in data

        if not is_modifying_access:
            return

        access = data.get("access", {})
        new_visibility = access.get("visibility")

        record_has_defined_access = "access" in record
        is_restricting = new_visibility == "restricted"

        if (
            VisibilityEnum(record.access.visibility) != VisibilityEnum(new_visibility)
            and record_has_defined_access
        ):
            self.service.require_permission(identity, "manage_access", record=record)
        if not record_has_defined_access and is_restricting:
            self.service.require_permission(
                identity, "create_restricted", record=record
            )

        record.setdefault("access", {})
        record["access"].update(access)
        record.access.refresh_from_dict(record.get("access"))

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the record."""
        self._populate_access_and_validate(identity, data, record, **kwargs)

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        self._populate_access_and_validate(identity, data, record, **kwargs)


class OwnershipComponent(ServiceComponent):
    """Service component for owner membership integration."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Make an owner member from the identity."""
        if system_process in identity.provides:
            return

        member = {
            "type": "user",
            "id": str(identity.id),
        }
        self.service.members.add(
            # the user is not yet owner of the community (is being added)
            # therefore we cannot use `identity`
            system_identity,
            record.id,
            {"members": [member], "role": current_roles.owner_role.name},
            uow=self.uow,
        )

        # Invalidate the membership cache
        on_user_membership_change(identity=identity)


class FeaturedCommunityComponent(ServiceComponent):
    """Service component for featured community integration."""

    def featured_create(self, identity, data=None, record=None, **kwargs):
        """Featured create."""
        if record.access.visibility != "public":
            raise ValidationError(
                _("The community is not public."), field_name="community_id"
            )


class OAISetComponent(ServiceComponent):
    """Service component for OAI set integration."""

    def _retrieve_set(self, slug):
        return OAISet.query.filter(OAISet.spec == self._create_set_spec(slug)).first()

    def _create_set_spec(self, community_slug):
        oai_sets_prefix = current_app.config["COMMUNITIES_OAI_SETS_PREFIX"]
        return "{prefix}{slug}".format(prefix=oai_sets_prefix, slug=community_slug)

    def _create_set_description(self, community_title):
        # NOTE: Does not require translation since this description can also be changed by an admin
        return "Records belonging to the community '{title}'".format(
            title=community_title
        )

    def _create_set_from_community(self, record):
        community_slug = record.slug
        community_title = record.metadata["title"]

        community_set = OAISet()
        community_set.name = community_title
        community_set.system_created = True
        community_set.description = self._create_set_description(community_title)
        community_set.spec = self._create_set_spec(community_slug)
        community_set.search_pattern = "parent.communities.ids:{id}".format(
            id=record.id
        )

        return community_set

    def create(self, identity, data=None, record=None, **kwargs):
        """Create a set for the community."""
        if record.access.visibility != "public":
            return

        community_set = self._create_set_from_community(record)
        # NOTE: will be indexed via a listener in oaiserver module
        db.session.add(community_set)

    def delete(self, identity, data=None, record=None, **kwargs):
        """Remove the set for the community."""
        community_set = self._retrieve_set(kwargs.get("slug") or record.slug)
        if not community_set:
            return

        # NOTE: will be removed from index via listener in oaiserver module
        db.session.delete(community_set)

    def update(self, identity, data=None, record=None, **kwargs):
        """Update set accordingly."""
        if record.access.visibility != "public":
            # delete set if the community is not public anymore
            self.delete(identity, data, record, **kwargs)
            return

        community_set = self._retrieve_set(record.slug)
        if not community_set:
            # create new set because community is now public
            self.create(identity, data, record, **kwargs)
            return

        # just update set with new name and description
        community_set.name = record.metadata["title"]
        community_set.description = self._create_set_description(community_set.name)
        db.session.add(community_set)

    def rename(self, identity, record=None, data=None, old_slug=None, **kwargs):
        """Delete old set and create new set on ID change."""
        if record.access.visibility != "public":
            return

        # Since we want to delete the set created with the old set, we can not
        # use the already updated pid_value
        self.delete(identity, data=data, record=record, **kwargs, slug=old_slug)
        community_set = self._create_set_from_community(record)
        db.session.add(community_set)


class CustomFieldsComponent(ServiceComponent):
    """Service component for custom fields."""

    def create(self, identity, data=None, record=None, errors=None, **kwargs):
        """Inject parsed custom fields to the record."""
        record.custom_fields = data.get("custom_fields", {})

    def update(self, identity, data=None, record=None, **kwargs):
        """Inject parsed custom fields to the record."""
        record.custom_fields = data.get("custom_fields", {})


class CommunityDeletionComponent(ServiceComponent):
    """Service component for record deletion."""

    def delete(self, identity, data=None, record=None, **kwargs):
        """Set the community's deletion status and tombstone information."""
        # Set the record's deletion status and tombstone information
        record.deletion_status = CommunityDeletionStatusEnum.DELETED
        record.tombstone = data

        # Set `removed_by` information for the tombstone
        record.tombstone.removed_by = identity.id

    def update_tombstone(self, identity, data=None, record=None, **kwargs):
        """Update the community's tombstone information."""
        record.tombstone = data

    def restore(self, identity, data=None, record=None, **kwargs):
        """Reset the community's deletion status and tombstone information."""
        record.deletion_status = CommunityDeletionStatusEnum.PUBLISHED

        # Remove the tombstone information
        record.tombstone = None

    def mark(self, identity, data=None, record=None, **kwargs):
        """Mark the community for purge."""
        record.deletion_status = CommunityDeletionStatusEnum.MARKED
        record.tombstone = record.tombstone

    def unmark(self, identity, data=None, record=None, **kwargs):
        """Unmark the community for purge, resetting it to soft-deleted state."""
        record.deletion_status = CommunityDeletionStatusEnum.DELETED
        record.tombstone = record.tombstone


class CommunityThemeComponent(ServiceComponent):
    """Service component for Community theme."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed theme to the record."""
        if "theme" in data:
            self.service.require_permission(identity, "set_theme", record=record)
            record["theme"] = data["theme"]

    def update(self, identity, data=None, record=None, errors=None, **kwargs):
        """Inject parsed theme to the record."""
        stored_record_theme = record.get("theme")
        if "theme" in data:
            # if theme set to None then it is a delete operation
            if data["theme"] is None:
                if stored_record_theme is not None:
                    self.service.require_permission(
                        identity, "delete_theme", record=record
                    )
                    # delete theme from record and data
                    record.pop("theme", None)
                # We always pop the {theme: None} from the data so we don't store None
                # value in the record
                data.pop("theme", None)
            elif data["theme"] != stored_record_theme:
                # check update permissions for theme only if incoming theme is
                # different from stored. Check is needed, so we don't apply the theme
                # permission check when other community information is updated
                self.service.require_permission(identity, "set_theme", record=record)
                record["theme"] = data["theme"]


class CommunityParentComponent(ServiceComponent):
    """Service Component for Community parent."""

    def _validate_and_get_parent(self, parent_data, child):
        """Validate and return parent community."""
        if not parent_data:
            return None
        try:
            parent = self.service.record_cls.pid.resolve(parent_data["id"])
            if not parent.children.allow:
                raise ValidationError("Assigned parent is not allowed to be a parent.")
            elif child.children.allow:
                raise ValidationError(
                    "Community allowed to be a parent can't be a child."
                )
            elif parent.parent:
                raise ValidationError(
                    "Assigned parent community cannot also have a parent."
                )
            elif child.id == parent.id:
                raise ValidationError(
                    "Assigned parent community cannot be the same as child."
                )
        except PIDDoesNotExistError:
            raise ValidationError("Assigned parent community does not exist.")
        return parent

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed theme to the record."""
        if "parent" in data:
            self.service.require_permission(identity, "manage_parent", record=record)
            parent = self._validate_and_get_parent(data["parent"], record)
            record.parent = parent

    def update(self, identity, data=None, record=None, **kwargs):
        """Update parent community of a community."""
        if "parent" in data:
            self.service.require_permission(identity, "manage_parent", record=record)
            parent = self._validate_and_get_parent(data["parent"], record)
            record.parent = parent


class ChildrenComponent(ServiceComponent):
    """Service component for children integration."""

    def _populate_and_validate(self, identity, data, record, **kwargs):
        """Populate and validate the community's children field."""
        # We check if data is passed and is different to the stored or default value
        existing_value = record.children.dump()
        if "children" in data and data["children"] != existing_value:
            self.service.require_permission(identity, "manage_children", record=record)
            record.children = record.children.from_dict(data["children"])

    def create(self, identity, data=None, record=None, **kwargs):
        """Create handler."""
        self._populate_and_validate(identity, data, record, **kwargs)

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        self._populate_and_validate(identity, data, record, **kwargs)


DefaultCommunityComponents = [
    MetadataComponent,
    CommunityThemeComponent,
    CustomFieldsComponent,
    PIDComponent,
    RelationsComponent,
    CommunityAccessComponent,
    OwnershipComponent,
    FeaturedCommunityComponent,
    OAISetComponent,
    CommunityDeletionComponent,
    ChildrenComponent,
    CommunityParentComponent,
]
