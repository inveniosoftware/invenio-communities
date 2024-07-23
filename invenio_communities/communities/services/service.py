# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
# Copyright (C) 2021-2022 Northwestern University.
# Copyright (C)      2022 Graz University of Technology.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Service API."""


from flask import current_app
from invenio_cache.decorators import cached_with_expiration
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.records import (
    RecordService,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordIndexOp,
    unit_of_work,
)
from invenio_requests import current_requests_service
from invenio_requests.services.results import EntityResolverExpandableField
from invenio_search.engine import dsl
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from invenio_communities.communities.records.models import CommunityFeatured
from invenio_communities.communities.services.links import CommunityLinksTemplate
from invenio_communities.communities.services.uow import (
    CommunityFeaturedCommitOp,
    CommunityFeaturedDeleteOp,
)
from invenio_communities.errors import (
    CommunityFeaturedEntryDoesNotExistError,
    LogoSizeLimitError,
    OpenRequestsForCommunityDeletionError,
)
from invenio_communities.generators import CommunityMembers

from ...errors import CommunityDeletedError, DeletionStatusError
from ..records.systemfields.deletion_status import CommunityDeletionStatusEnum


class CommunityService(RecordService):
    """community Service."""

    def __init__(
        self, config, files_service=None, invitations_service=None, members_service=None
    ):
        """Constructor for CommunityService."""
        super().__init__(config)
        self._files = files_service
        self._invitations = invitations_service
        self._members = members_service

    @property
    def links_item_tpl(self):
        """Item links template."""
        return CommunityLinksTemplate(
            self.config.links_item,
            self.config.action_link,
            self.config.available_actions,
            context={
                "permission_policy_cls": self.config.permission_policy_cls,
            },
        )

    @property
    def files(self):
        """Community files service."""
        return self._files

    @property
    def invitations(self):
        """Community invitations service."""
        return self._invitations

    @property
    def members(self):
        """Community members service."""
        return self._members

    @property
    def schema_featured(self):
        """Returns the featured data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_featured)

    @property
    def schema_tombstone(self):
        """Returns the tombstone data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_tombstone)

    @property
    def expandable_fields(self):
        """Get expandable fields."""
        return [
            EntityResolverExpandableField("created_by"),
            EntityResolverExpandableField("receiver"),
        ]

    def search_user_communities(
        self, identity, params=None, search_preference=None, extra_filter=None, **kwargs
    ):
        """Search for records matching the querystring."""
        self.require_permission(identity, "search_user_communities")

        # Prepare and execute the search
        params = params or {}

        current_user_filter = CommunityMembers().query_filter(identity)
        undeleted_filter = dsl.Q(
            "term", **{"deletion_status": CommunityDeletionStatusEnum.PUBLISHED.value}
        )

        search_filter = current_user_filter & undeleted_filter

        if extra_filter:
            search_filter &= extra_filter

        search_result = self._search(
            "search",
            identity,
            params,
            search_preference,
            extra_filter=search_filter,
            permission_action="read",
            **kwargs,
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_user_search, context={"args": params}
            ),
            links_item_tpl=self.links_item_tpl,
        )

    def search_community_requests(
        self,
        identity,
        community_id,
        params=None,
        search_preference=None,
        expand=False,
        **kwargs,
    ):
        """Search for requests of a specific community."""
        self.require_permission(identity, "search_requests", community_id=community_id)

        # Prepare and execute the search
        params = params or {}
        search_result = current_requests_service._search(
            "search",
            identity,
            params,
            search_preference,
            permission_action=None,
            extra_filter=dsl.Q(
                "bool",
                must=[
                    dsl.Q("term", **{"receiver.community": community_id}),
                    ~dsl.Q("term", **{"status": "created"}),
                ],
            ),
            **kwargs,
        ).execute()

        return current_requests_service.result_list(
            current_requests_service,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_community_requests_search,
                context={"args": params, "community_id": community_id},
            ),
            links_item_tpl=current_requests_service.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def rename(
        self, identity, id_, data, revision_id=None, raise_errors=True, uow=None
    ):
        """Rename a community."""
        record = self.record_cls.pid.resolve(id_)
        old_slug = record.slug

        self.check_revision_id(record, revision_id)

        # Permissions
        self.require_permission(identity, "rename", record=record)

        if "slug" not in data:
            raise ValidationError(
                "Missing data for required field.",
                field_name="slug",
            )

        data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,  # if False, flow is continued with
            schema_args={"partial": True},  # data only containing valid data,
            # but errors are reported
        )  # (as warnings)

        # Run components
        self.run_components(
            "rename", identity, data=data, record=record, old_slug=old_slug, uow=uow
        )

        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def read_logo(self, identity, id_):
        """Read the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "read", record=record)
        logo_file = record.files.get("logo")
        if logo_file is None:
            raise FileNotFoundError()
        return self.files.file_result_item(
            self.files,
            identity,
            logo_file,
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    @unit_of_work()
    def update_logo(self, identity, id_, stream, content_length=None, uow=None):
        """Update the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "update", record=record)

        logo_size_limit = 10**6
        max_size = current_app.config["COMMUNITIES_LOGO_MAX_FILE_SIZE"]
        if type(max_size) is int and max_size > 0:
            logo_size_limit = max_size

        if content_length and content_length > logo_size_limit:
            raise LogoSizeLimitError(logo_size_limit, content_length)

        record.files["logo"] = stream
        uow.register(RecordCommitOp(record))

        return self.files.file_result_item(
            self.files,
            identity,
            record.files["logo"],
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    @unit_of_work()
    def delete_logo(self, identity, id_, uow=None):
        """Delete the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        # update permission on community is required to be able to remove logo.
        self.require_permission(identity, "update", record=record)
        deleted_file = record.files.pop("logo", None)
        if deleted_file is None:
            raise FileNotFoundError()

        deleted_file.delete(force=True)

        uow.register(RecordCommitOp(record))

        return self.files.file_result_item(
            self.files,
            identity,
            deleted_file,
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    def _get_featured_entry(self, raise_error=True, **kwargs):
        """Retrieve featured entry based on provided arguments."""
        errors = []
        try:
            featured_entry = CommunityFeatured.query.filter_by(**kwargs).one()
        except NoResultFound as e:
            if raise_error:
                raise CommunityFeaturedEntryDoesNotExistError(kwargs)
            featured_entry = None
            errors.append(str(e))

        return featured_entry, errors

    def featured_search(self, identity, params=None, search_preference=None, **kwargs):
        """Search featured communities."""
        self.require_permission(identity, "search")

        # Prepare and execute the search
        params = params or {}
        params["sort"] = "featured"

        search_results = self._search(
            "search",
            identity,
            params,
            search_preference,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("match", **{"access.visibility": "public"}),
                    dsl.Q("exists", **{"field": "featured.past"}),
                ],
            ),
            permission_action="featured_search",
            **kwargs,
        ).execute()
        return self.result_list(
            self,
            identity,
            search_results,
            params=params,
            links_tpl=LinksTemplate(
                self.config.links_featured_search, context={"args": params}
            ),
            links_item_tpl=self.links_item_tpl,
        )

    def featured_list(self, identity, community_id):
        """List featured entries for a community."""
        record = self.record_cls.pid.resolve(community_id)

        # Permissions
        self.require_permission(identity, "featured_list", record=record)

        featured_entries = CommunityFeatured.query.filter(
            CommunityFeatured.community_id == record.id,
        ).paginate(
            per_page=1000,
        )

        return self.config.result_list_cls_featured(
            self,
            identity,
            featured_entries,
            links_tpl=LinksTemplate(self.config.links_featured_search),
            schema=self.schema_featured,
        )

    @unit_of_work()
    def featured_create(
        self, identity, community_id, data, raise_errors=True, uow=None
    ):
        """Create a featured entry for a community."""
        record = self.record_cls.pid.resolve(community_id)

        # Permissions
        self.require_permission(identity, "featured_create", record=record)

        data, errors = self.schema_featured.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        featured_entry = CommunityFeatured(**data)
        featured_entry.community_id = record.id

        # Run components
        self.run_components(
            "featured_create", identity, data=data, record=record, uow=uow
        )

        uow.register(CommunityFeaturedCommitOp(featured_entry))
        uow.register(RecordIndexOp(record, indexer=self.indexer, index_refresh=True))

        return self.result_item(
            self,
            identity,
            featured_entry,
            schema=self.schema_featured,
        )

    @unit_of_work()
    def featured_update(
        self, identity, community_id, data, featured_id, raise_errors=True, uow=None
    ):
        """Update a featured entry for a community."""
        record = self.record_cls.pid.resolve(community_id)
        featured_entry, _ = self._get_featured_entry(
            id=featured_id,
            community_id=record.id,
        )

        self.require_permission(identity, "featured_update", record=record)

        valid_data, errors = self.schema_featured.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        # Run components
        self.run_components(
            "featured_update", identity, data=valid_data, record=record, uow=uow
        )

        for key, value in valid_data.items():
            setattr(featured_entry, key, value)

        uow.register(CommunityFeaturedCommitOp(featured_entry))
        uow.register(RecordIndexOp(record, indexer=self.indexer, index_refresh=True))

        return self.result_item(
            self,
            identity,
            featured_entry,
            schema=self.schema_featured,
        )

    @unit_of_work()
    def featured_delete(
        self, identity, community_id, featured_id, raise_errors=True, uow=None
    ):
        """Delete a featured entry for a community."""
        record = self.record_cls.pid.resolve(community_id)
        featured_entry, _ = self._get_featured_entry(
            id=featured_id,
            community_id=record.id,
        )

        self.require_permission(identity, "featured_delete", record=record)

        # Run components
        self.run_components(
            "featured_delete", identity, data=None, record=record, uow=uow
        )

        uow.register(CommunityFeaturedDeleteOp(featured_entry))
        uow.register(RecordIndexOp(record, indexer=self.indexer, index_refresh=True))

        return

    #
    # Deletion workflows
    #
    @unit_of_work()
    def delete_community(
        self, identity, id_, data=None, revision_id=None, expand=False, uow=None
    ):
        """(Soft) delete a published community."""
        record = self.record_cls.pid.resolve(id_)
        # Check permissions
        self.require_permission(identity, "delete", record=record)
        self.check_revision_id(record, revision_id)

        if record.deletion_status.is_deleted:
            raise DeletionStatusError(record, CommunityDeletionStatusEnum.PUBLISHED)

        # check if requests are open
        requests = self.search_community_requests(
            identity, record.id, {"is_open": True}
        )
        if len(requests) > 0:
            raise OpenRequestsForCommunityDeletionError(len(requests))

        # Load tombstone data with the schema
        data, errors = self.schema_tombstone.load(
            data or {},
            context={
                "identity": identity,
                "pid": record.pid,
                "record": record,
            },
            raise_errors=True,
        )

        # Run components
        self.run_components("delete", identity, data=data, record=record, uow=uow)

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def delete(
        self, identity, id_, data=None, expand=False, revision_id=None, uow=None
    ):
        """Alias for ``delete_community()``."""
        return self.delete_community(
            identity, id_, data, revision_id=revision_id, expand=expand, uow=uow
        )

    @unit_of_work()
    def update_tombstone(self, identity, id_, data, expand=False, uow=None):
        """Update the tombstone information for the (soft) deleted community."""
        record = self.record_cls.pid.resolve(id_)
        if not record.deletion_status.is_deleted:
            # strictly speaking, it's two expected statuses: DELETED or MARKED
            raise DeletionStatusError(record, CommunityDeletionStatusEnum.DELETED)

        # Check permissions
        self.require_permission(identity, "delete", record=record)

        # Load tombstone data with the schema and set it
        data, errors = self.schema_tombstone.load(
            data,
            context={
                "identity": identity,
                "pid": record.pid,
                "record": record,
            },
            raise_errors=True,
        )

        # Run components
        self.run_components(
            "update_tombstone", identity, data=data, record=record, uow=uow
        )

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def restore_community(self, identity, id_, expand=False, uow=None):
        """Restore a record that has been (soft) deleted."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status != CommunityDeletionStatusEnum.DELETED:
            raise DeletionStatusError(CommunityDeletionStatusEnum.DELETED, record)

        # Check permissions
        self.require_permission(identity, "delete", record=record)

        # Run components
        self.run_components("restore", identity, record=record, uow=uow)

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def mark_community_for_purge(self, identity, id_, expand=False, uow=None):
        """Mark a (soft) deleted record for purge."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status != CommunityDeletionStatusEnum.DELETED:
            raise DeletionStatusError(record, CommunityDeletionStatusEnum.DELETED)

        # Check permissions
        self.require_permission(identity, "purge", record=record)

        # Run components
        self.run_components("mark", identity, record=record, uow=uow)

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def unmark_community_for_purge(self, identity, id_, expand=False, uow=None):
        """Remove the mark for deletion from a record, returning it to deleted state."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status != CommunityDeletionStatusEnum.MARKED:
            raise DeletionStatusError(record, CommunityDeletionStatusEnum.MARKED)

        # Check permissions
        self.require_permission(identity, "purge", record=record)

        # Run components
        self.run_components("unmark", identity, record=record, uow=uow)

        # Commit and reindex the record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def purge_community(self, identity, id_, uow=None):
        """Purge a record that has been marked."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status != CommunityDeletionStatusEnum.MARKED:
            raise DeletionStatusError(record, CommunityDeletionStatusEnum.MARKED)

        raise NotImplementedError()

    #
    # Search functions
    #
    def search(
        self,
        identity,
        params=None,
        search_preference=None,
        expand=False,
        extra_filter=None,
        **kwargs,
    ):
        """Search for published communities matching the querystring."""
        return super().search(
            identity,
            params,
            search_preference,
            expand,
            extra_filter=extra_filter,
            # injects deleted records when user is permitted to see them
            permission_action="read_deleted",
            **kwargs,
        )

    #
    # Base methods, extended with handling of deleted records
    #
    def read(self, identity, id_, expand=False, include_deleted=False):
        """Retrieve a record."""
        record = self.record_cls.pid.resolve(id_)
        result = super().read(identity, id_, expand=expand)
        if not include_deleted and record.deletion_status.is_deleted:
            raise CommunityDeletedError(record, result_item=result)
        if include_deleted and record.deletion_status.is_deleted:
            can_read_deleted = self.check_permission(
                identity, "read_deleted", record=record
            )

            if not can_read_deleted:
                # displays tombstone
                raise CommunityDeletedError(record, result_item=result)

        return result

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None, expand=False):
        """Replace a record."""
        record = self.record_cls.pid.resolve(id_)

        if record.deletion_status.is_deleted:
            raise CommunityDeletedError(
                record,
                result_item=self.result_item(
                    self,
                    identity,
                    record,
                    links_tpl=self.links_item_tpl,
                    expandable_fields=self.expandable_fields,
                    expand=expand,
                ),
            )

        return super().update(
            identity, id_, data, revision_id=revision_id, uow=uow, expand=expand
        )

    #
    # notification handlers
    #
    def on_relation_update(self, identity, record_type, records_info, notif_time):
        """Relation updates notification handler."""
        if self.members:
            self.members.on_relation_update(
                identity, record_type, records_info, notif_time
            )
        if self.invitations:
            self.invitations.on_relation_update(
                identity, record_type, records_info, notif_time
            )

        return True

    @unit_of_work()
    def bulk_update_parent(self, identity, community_ids, parent_id, uow=None):
        """Bulk updates communities with a new parent.

        :param identity: The identity of the user performing the action.
        :param community_ids: The list of community IDs to add to the new parent.
        :param parent_id: The ID of the new parent community.
        """
        parent = self.read(identity, parent_id)
        for comm_id in community_ids:
            child = self.read(identity, comm_id)
            self.update(
                identity,
                comm_id,
                data={**child.data, "parent": {"id": parent.id}},
                uow=uow,
            )
        return True


@cached_with_expiration
def get_cached_community_slug(
    community_id,
    community_service_id="communities",
):
    """Cache community's slug.

    :param community_id: the UUID of the community's record.
    :param community_service_id: the id of the service registered in the service
        register, in case it have been overridden.

    Note: this by-passes any permission check, use it with caution!

    Useful when the community's slug should be resolved for each hit of search results,
    without impacting performance.
    """
    community_service = current_service_registry.get(community_service_id)
    community_cls = community_service.record_cls
    return community_cls.pid.resolve(community_id).slug
