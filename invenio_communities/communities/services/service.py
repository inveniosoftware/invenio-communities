# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities Service API."""

from elasticsearch_dsl import Q
from invenio_db import db
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.records import RecordService
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from marshmallow.exceptions import ValidationError


class CommunityService(RecordService):
    """community Service."""

    def __init__(self, config, files_service=None):
        """Constructor for CommunityService."""
        super().__init__(config)
        self._files = files_service

    @property
    def files(self):
        """Community files service."""
        return self._files

    def search_user_communities(
            self, identity, params=None, es_preference=None, **kwargs):
        """Search for records matching the querystring."""
        self.require_permission(identity, 'search_user_communities')

        # Prepare and execute the search
        params = params or {}
        search_result = self._search(
            'search',
            identity,
            params,
            es_preference,
            extra_filter=Q(
                "term",
                **{"access.owned_by.user": identity.id}
            ),
            permission_action='read',
            **kwargs).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(self.config.links_user_search, context={
                "args": params
            }),
            links_item_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def rename(self, id_, identity, data, revision_id=None, raise_errors=True,
               uow=None):
        """Rename a community."""
        record = self.record_cls.pid.resolve(id_)

        self.check_revision_id(record, revision_id)

        # Permissions
        self.require_permission(identity, "rename", record=record)

        if 'id' not in data:
            raise ValidationError(
                'Missing data for required field.',
                field_name='id',
            )

        data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,     # if False, flow is continued with
            schema_args={'partial': True}  # data only containing valid data,
                                           # but errors are reported
        )                                  # (as warnings)

        # Run components
        self.run_components(
            'rename', identity, data=data, record=record, uow=uow)

        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def read_logo(self, id_, identity):
        """Read the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, 'read', record=record)
        logo_file = record.files.get('logo')
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
    def update_logo(self, id_, identity, stream, content_length=None,
                    uow=None):
        """Update the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, 'update', record=record)

        record.files['logo'] = stream
        uow.register(RecordCommitOp(record))

        return self.files.file_result_item(
            self.files,
            identity,
            record.files['logo'],
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )

    @unit_of_work()
    def delete_logo(self, id_, identity, uow=None):
        """Delete the community's logo."""
        record = self.record_cls.pid.resolve(id_)
        deleted_file = record.files.pop('logo', None)
        if deleted_file is None:
            raise FileNotFoundError()

        uow.register(RecordCommitOp(record))

        return self.files.file_result_item(
            self.files,
            identity,
            deleted_file,
            record,
            links_tpl=self.files.file_links_item_tpl(id_),
        )
