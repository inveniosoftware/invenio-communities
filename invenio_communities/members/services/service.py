# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Service."""

from invenio_records_resources.services.records import RecordService
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work


class MemberService(RecordService):
    """Member Service."""

    def _to_id(self, data):
        """Convert data dict to dict of primary keys."""
        # TODO: add group
        return {
            "community_id": data.get("community"),
            "user_id": data.get("user"),
        }

    @unit_of_work()
    def create(self, identity, data, uow=None):
        """Create member."""
        # TODO: Check permission
        # self.require_permission(identity, "create")

        # Validate data (if there are errors, .load() raises)
        data, errors = self.schema.load(
            data,
            context={"identity": identity},
        )

        member_record = self.record_cls.create(
            {},
            community_id=data.get("community"),
            user_id=data.get("user"),
            role=data.get("role")
        )

        # Persist record (DB and index)
        uow.register(RecordCommitOp(member_record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            member_record,
            links_tpl=self.links_item_tpl,
        )

    def read(self, identity, id_):
        """Read member record.

        :param id_: a dict of the primary keys
        """
        member_record = self.record_cls.get_record(self._to_id(id_))

        # TODO: Permission
        # self.require_permission(identity, "read", record=member_record)

        return self.result_item(
            self,
            identity,
            member_record,
            links_tpl=self.links_item_tpl,
        )
