# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members service."""

from datetime import datetime, timezone

from elasticsearch_dsl.query import Q
from flask import current_app
from flask_babelex import gettext as _
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.records import (
    RecordService,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.uow import (
    IndexRefreshOp,
    RecordCommitOp,
    RecordDeleteOp,
    unit_of_work,
)
from invenio_requests import current_events_service, current_requests_service
from invenio_requests.customizations.event_types import CommentEventType
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from invenio_communities.members.records.api import ArchivedInvitation

from ...proxies import current_roles
from ..errors import AlreadyMemberError, InvalidMemberError
from .request import CommunityInvitation
from .schemas import (
    AddBulkSchema,
    DeleteBulkSchema,
    InvitationDumpSchema,
    InviteBulkSchema,
    MemberDumpSchema,
    PublicDumpSchema,
    UpdateBulkSchema,
)


def invite_expires_at():
    """Get the invitation expiration date."""
    return (
        datetime.utcnow().replace(tzinfo=timezone.utc)
        + current_app.config["COMMUNITIES_INVITATIONS_EXPIRES_IN"]
    )


class MemberService(RecordService):
    """Community members service."""

    @property
    def community_cls(self):
        """Return community class."""
        return self.config.community_cls

    @property
    def member_dump_schema(self):
        """Schema for creation."""
        return ServiceSchemaWrapper(self, schema=MemberDumpSchema)

    @property
    def public_dump_schema(self):
        """Schema for creation."""
        return ServiceSchemaWrapper(self, schema=PublicDumpSchema)

    @property
    def invitation_dump_schema(self):
        """Schema for creation."""
        return ServiceSchemaWrapper(self, schema=InvitationDumpSchema)

    @property
    def add_schema(self):
        """Schema for creation."""
        return ServiceSchemaWrapper(self, schema=AddBulkSchema)

    @property
    def invite_schema(self):
        """Schema for creation."""
        return ServiceSchemaWrapper(self, schema=InviteBulkSchema)

    @property
    def update_schema(self):
        """Schema for bulk update."""
        return ServiceSchemaWrapper(self, schema=UpdateBulkSchema)

    @property
    def delete_schema(self):
        """Schema for bulk delete."""
        return ServiceSchemaWrapper(self, schema=DeleteBulkSchema)

    @property
    def archive_indexer(self):
        """Factory for creating an indexer instance."""
        return self.config.indexer_cls(
            record_cls=ArchivedInvitation,
            record_to_index=self.record_to_index,
            record_dumper=self.config.index_dumper,
        )

    #
    # Add and invite
    #
    @unit_of_work()
    def add(self, identity, community_id, data, uow=None):
        """Add group members.

        The default permission policy only allow groups to be added. Users must
        be invited.
        """
        ret = self._create(
            identity,
            community_id,
            data,
            self.add_schema,
            "members_add",
            self._add_factory,
            uow,
        )
        # ensure index is refreshed to search for newly added members
        uow.register(IndexRefreshOp(indexer=self.indexer))
        return ret

    @unit_of_work()
    def invite(self, identity, community_id, data, uow=None):
        """Invite group members.

        Only users and email member types can be invited, and a member can only
        have one invitation per community

        Email member type is not yet supported.
        """
        ret = self._create(
            identity,
            community_id,
            data,
            self.invite_schema,
            "members_invite",
            self._invite_factory,
            uow,
        )

        # ensure index is refreshed to search for newly added members
        uow.register(IndexRefreshOp(indexer=self.indexer))
        return ret

    def _create(self, identity, community_id, data, schema, action, factory, uow):
        """Internal method used for both adding and inviting users/groups.

        The methods are shared because adding and inviting users/groups share
        the most of the same permission and integrity checks.
        """
        community = self.community_cls.get_record(community_id)
        # Validate data (if there are errors, .load() raises)
        data, errors = schema.load(
            data,
            context={"identity": identity},
        )
        role = data["role"]
        members = data["members"]
        member_types = {m["type"] for m in data["members"]}
        message = data.get("message")
        # Users are expected to explicitly change their visibility themselves
        # due to data privacy concerns.
        # The system identity can set the visible property to support data
        # migration use cases.
        visible = data.get("visible", False)
        if visible and identity != system_identity:
            raise ValidationError(_("Must be false"))

        # Permission checks - validates that:
        # - identity has permission to manage members
        # - identity has permission to add/invite for a given role (e.g.
        #   managers should not be able to invite owners because it would make
        #   privilege escalation possible).
        # - identity is allowed to create a specific member type (e.g. usually
        #   we only allow adding groups, and inviting users/emails however in
        #   a migration use case we may want to allow adding users directly).
        self.require_permission(
            identity,
            action,
            record=community,
            role=role.name,
            member_types=member_types,
        )

        # Add/invite members via the factory function.
        for m in members:
            # TODO: Add support for inviting an email
            if m["type"] == "email":
                raise ValidationError(_("Invalid member type: email"))

            factory(identity, community, role, visible, m, message, uow)

        return True

    def _add_factory(
        self,
        identity,
        community,
        role,
        visible,
        member,
        message,
        uow,
        active=True,
        request_id=None,
    ):
        """Add a member to the community."""
        # TODO: inefficient to do here, should be done in bulk instead.
        if member["type"] == "group":
            try:
                # member['id'] is mapped from role.name
                # (check invenio-users-resources)
                member["id"] = Role.query.filter_by(name=member["id"]).one().id
            except NoResultFound as e:
                raise InvalidMemberError(member) from e

        member_arg = {member["type"] + "_id": member["id"]}
        try:
            # Integrity checks happens here which will validate:
            # - if a user/group is already a member
            # - if a user is already invited
            member = self.record_cls.create(
                {},
                community_id=community.id,
                role=role.name,
                active=active,
                visible=visible,
                request_id=request_id,
                **member_arg
            )
        except IntegrityError as e:
            raise AlreadyMemberError() from e

        # TODO: Change this to bulk index all member records in one request
        # instead of N single indexing requests.
        uow.register(RecordCommitOp(member, indexer=self.indexer))

    def _invite_factory(self, identity, community, role, visible, member, message, uow):
        """Invite a member to the community."""
        if member["type"] == "group":
            # Groups cannot be invited, because groups have no one who can
            # accept an invitation.
            raise InvalidMemberError(member)

        # Add member entry
        if member["type"] == "user":
            # Create request
            title = _('Invitation to join "{community}"').format(
                community=community.metadata["title"],
            )

            request_item = current_requests_service.create(
                identity,
                {"title": title},
                CommunityInvitation,
                {"user": member["id"]},
                creator=community,
                # TODO: perhaps topic should be the actual membership record
                # instead
                topic=community,
                expires_at=invite_expires_at(),
                uow=uow,
            )

            # add role as message
            data = {
                "payload": {
                    "content": _('You will join as "{role}".').format(role=role.title),
                }
            }
            current_events_service.create(
                identity, request_item.id, data, CommentEventType, uow=uow
            )
            # message was provided.
            if message:
                data = {"payload": {"content": message}}
                current_events_service.create(
                    identity, request_item.id, data, CommentEventType, uow=uow
                )

            # Create an inactive member entry linked to the request.
            self._add_factory(
                identity,
                community,
                role,
                visible,
                member,
                message,
                uow,
                active=False,
                request_id=request_item.id,
            )

    def search(self, identity, community_id, params=None, es_preference=None, **kwargs):
        """Search."""
        return self._members_search(
            identity,
            community_id,
            "members_search",
            self.member_dump_schema,
            self.config.search,
            extra_filter=Q("term", **{"active": True}),
            params=params,
            es_preference=es_preference,
            **kwargs
        )

    def search_public(
        self, identity, community_id, params=None, es_preference=None, **kwargs
    ):
        """Search public members matching the querystring."""
        # The search for members is split two methods (public, members) to
        # prevent leaking of information. E.g. the public serialization
        # must now have all fields present.
        # TODO: limit fields on which the query works on to avoid leaking
        # information
        return self._members_search(
            identity,
            community_id,
            "members_search_public",
            self.public_dump_schema,
            self.config.search_public,
            extra_filter=(
                Q("term", **{"visible": True}) & Q("term", **{"active": True})
            ),
            params=params,
            es_preference=es_preference,
            **kwargs
        )

    def search_invitations(
        self, identity, community_id, params=None, es_preference=None, **kwargs
    ):
        """Search invitations."""
        # The search for invitations used the ArchivedInvitation record class
        # which will search over the "communitymembers" alias which include
        # both current invitations and archived invitations.
        return self._members_search(
            identity,
            community_id,
            "search_invites",
            self.invitation_dump_schema,
            self.config.search_invitations,
            record_cls=ArchivedInvitation,
            extra_filter=Q("term", **{"active": False}),
            params=params,
            es_preference=es_preference,
            **kwargs
        )

    def _members_search(
        self,
        identity,
        community_id,
        permission_action,
        schema,
        search_opts,
        extra_filter=None,
        params=None,
        es_preference=None,
        **kwargs
    ):
        """Members search."""
        community = self.community_cls.get_record(community_id)
        self.require_permission(identity, permission_action, record=community)

        # Apply extra filters
        filter = Q("term", **{"community_id": community.id})
        if extra_filter:
            filter &= extra_filter

        # Prepare and execute the search
        params = params or {}

        search = self._search(
            "search_members",
            identity,
            params,
            es_preference,
            search_opts=search_opts,
            permission_action=None,
            extra_filter=filter,
            **kwargs
        )
        search_result = search.execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search,
                context={
                    "args": params,
                    "community_id": community_id,
                },
            ),
            schema=schema,
        )

    @unit_of_work()
    def update(self, identity, community_id, data, uow=None, refresh=False):
        """Bulk update.

        Used to update both active members and active invitations. Archived
        invitations cannot be updated.
        """
        community = self.community_cls.get_record(community_id)

        # Permission check - validates that:
        # - identity has permission to change any member at all (incl self)
        self.require_permission(
            identity,
            "members_bulk_update",
            record=community,
        )

        # Validate data (if there are errors, .load() raises)
        data, errors = self.update_schema.load(
            data,
            context={"identity": identity},
        )

        # Schema validates that role and/or visibility are defined.
        members = self.record_cls.get_members(community.id, members=data["members"])
        if len(members) != len(data["members"]):
            raise InvalidMemberError()
        role = data.get("role")
        visible = data.get("visible")

        # Perform updates (and check permissions)
        for m in members:
            self._update(identity, community, m, role, visible, uow)

        # Make sure we're not left owner-less if a role was changed.
        if role is not None:
            if not self.record_cls.has_members(
                community_id, role=current_roles.owner_role.name
            ):
                raise ValidationError(
                    _("A community must have at least one owner."),
                )

        if refresh:
            uow.register(IndexRefreshOp(indexer=self.indexer))

        return True

    def _update(self, identity, community, member, role, visible, uow):
        """Update a member's role/visibility."""
        # DO NOT USE DIRECTLY - always use update() which will correctly check
        # if we're left without an owner!
        self.require_permission(
            identity,
            "members_update",
            record=community,
            member=member,
            role=role.name if role is not None else None,
        )
        is_self = identity.id is not None and str(member.user_id) == str(identity.id)

        # Pre-conditions:
        # You cannot change your own role (owners, managers, members = all)
        # For owners/managers, this prevents them accidentally loosing access.
        # They will have to ask another owner/manager to change their role.
        # For curators/readers, they should not be be allowed to change their
        # own role. Having a business rule avoid making the permissions overly
        # complex.
        if role is not None and is_self:
            raise ValidationError(_("You cannot change your own role."))

        # Owners/managers can change visibility to false for users, and
        # true/false for groups. Users themselves can change their own
        # visibility. System identity can can always change for all.
        if visible is not None and member.user_id is not None:
            if visible and not (is_self or system_identity == identity):
                raise ValidationError(
                    _("You can only set public visibility on your own membership."),
                )

        # Update membership
        if role is not None:
            if not member.active:  # still an invitation
                data = {
                    "payload": {
                        "content": _(
                            'You will join as "{role}" (changed from: "{previous}").'
                        ).format(
                            role=role.title,
                            previous=member.role,
                        ),
                    }
                }
                current_events_service.create(
                    identity, member.request_id, data, CommentEventType, uow=uow
                )

            # update role
            member.role = role.name
        if visible is not None:
            member.visible = visible

        uow.register(RecordCommitOp(member, self.indexer))

        return True

    @unit_of_work()
    def delete(self, identity, community_id, data, uow=None):
        """Bulk delete."""
        community = self.community_cls.get_record(community_id)

        # Permission check - validates that:
        # - identity has permission to delete any member at all (incl self)
        self.require_permission(
            identity,
            "members_bulk_delete",
            record=community,
        )

        # Validate data (if there are errors, .load() raises)
        data, errors = self.delete_schema.load(
            data,
            context={"identity": identity},
        )
        members = self.record_cls.get_members(community.id, members=data["members"])
        if len(members) != len(data["members"]):
            raise InvalidMemberError()

        # Perform deletes (and check permissions)
        for m in members:
            self.require_permission(
                identity,
                "members_delete",
                record=community,
                member=m,
            )
            uow.register(RecordDeleteOp(m, self.indexer, force=True))

        # Make sure we're not left owner-less
        if not self.record_cls.has_members(
            community_id, role=current_roles.owner_role.name
        ):
            raise ValidationError(
                _("A community must have at least one owner."),
            )

        return True

    @unit_of_work()
    def accept_invite(self, identity, request_id, uow=None):
        """Accept an invitation."""
        # Permissions are checked on the request action
        assert identity == system_identity
        member = self.record_cls.get_member_by_request(request_id)
        assert member.active is False
        archived_invitation = ArchivedInvitation.create_from_member(member)
        member.active = True
        # TODO: recompute permissions for member.
        uow.register(RecordCommitOp(member, indexer=self.indexer))
        uow.register(RecordCommitOp(archived_invitation, indexer=self.archive_indexer))
        uow.register(IndexRefreshOp(indexer=self.indexer))

    @unit_of_work()
    def decline_invite(self, identity, request_id, uow=None):
        """Decline an invitation."""
        # Permissions are checked on the request action
        assert identity == system_identity
        member = self.record_cls.get_member_by_request(request_id)
        assert member.active is False
        archived_invitation = ArchivedInvitation.create_from_member(member)
        uow.register(RecordDeleteOp(member, indexer=self.indexer, force=True))
        uow.register(RecordCommitOp(archived_invitation, indexer=self.archive_indexer))
        uow.register(
            IndexRefreshOp(
                # need to use an indexer with a diff index
                # no access to invitations indexer
                indexer=self.indexer,
                index=ArchivedInvitation.index,
            )
        )

    def read_many(self, *args, **kwargs):
        """Not implemented."""
        raise NotImplementedError("Use search() or search_public()")

    def read_all(self, *args, **kwargs):
        """Not implemented."""
        raise NotImplementedError("Use search() or search_public()")

    def read(self, *args, **kwargs):
        """Not implemented."""
        raise NotImplementedError("Use search() or search_public()")

    def create(self, *args, **kwargs):
        """Not implemented."""
        raise NotImplementedError("Use add() or invite()")

    def rebuild_index(self, identity, uow=None):
        """Reindex all records managed by this service.

        Note: Skips (soft) deleted records.
        """
        for rec_meta in self.record_cls.model_cls.query.all():
            rec = self.record_cls(rec_meta.data, model=rec_meta)

            if not rec.is_deleted:
                self.indexer.index(rec)

        for rec_meta in ArchivedInvitation.model_cls.query.all():
            rec = ArchivedInvitation(rec_meta.data, model=rec_meta)

            if not rec.is_deleted:
                self.indexer.index(rec)

        return True
