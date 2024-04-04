# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import ConstantField, DictField, ModelField
from invenio_records.systemfields.relations import MultiRelationsField
from invenio_records_resources.records.api import FileRecord, Record
from invenio_records_resources.records.systemfields import (
    FilesField,
    IndexField,
    PIDListRelation,
    PIDRelation,
)
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.systemfields.relations import CustomFieldsRelation

from invenio_communities.communities.records.systemfields.children import ChildrenField
from invenio_communities.communities.records.systemfields.is_verified import (
    IsVerifiedField,
)

from ..dumpers.featured import FeaturedDumperExt
from . import models
from .systemfields.access import CommunityAccessField
from .systemfields.deletion_status import CommunityDeletionStatusField
from .systemfields.parent_community import ParentCommunityField
from .systemfields.pidslug import PIDSlugField
from .systemfields.tombstone import TombstoneField


class CommunityFile(FileRecord):
    """Community file API."""

    model_cls = models.CommunityFileMetadata
    record_cls = None  # defined below


class Community(Record):
    """Community API."""

    id = ModelField()
    slug = ModelField()
    pid = PIDSlugField("id", "slug")
    parent = ParentCommunityField()
    children = ChildrenField()

    schema = ConstantField("$schema", "local://communities/communities-v1.0.0.json")

    model_cls = models.CommunityMetadata

    dumper = SearchDumper(
        extensions=[
            FeaturedDumperExt("featured"),
            RelationDumperExt("relations"),
        ]
    )

    index = IndexField("communities-communities-v1.0.0", search_alias="communities")

    access = CommunityAccessField()

    #: Custom fields system field.
    custom_fields = DictField(clear_none=True, create_if_missing=True)
    theme = DictField(clear_none=True)

    bucket_id = ModelField(dump=False)
    bucket = ModelField(dump=False)
    files = FilesField(
        store=False,
        file_cls=CommunityFile,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    relations = MultiRelationsField(
        funding_award=PIDListRelation(
            "metadata.funding",
            relation_field="award",
            keys=["title", "number", "identifiers", "acronym", "program"],
            pid_field=Award.pid,
            cache_key="awards",
        ),
        funding_funder=PIDListRelation(
            "metadata.funding",
            relation_field="funder",
            keys=["name"],
            pid_field=Funder.pid,
            cache_key="funders",
        ),
        organizations=PIDListRelation(
            "metadata.organizations",
            keys=["name"],
            pid_field=Affiliation.pid,
            cache_key="affiliations",
        ),
        type=PIDRelation(
            "metadata.type",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("communitytypes"),
            cache_key="communitytypes",
        ),
        removal_reason=PIDRelation(
            "tombstone.removal_reason",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("removalreasons"),
            cache_key="removal_reason",
        ),
        custom=CustomFieldsRelation("COMMUNITIES_CUSTOM_FIELDS"),
    )

    is_verified = IsVerifiedField("is_verified", use_cache=True, index=True)

    deletion_status = CommunityDeletionStatusField()

    tombstone = TombstoneField()


CommunityFile.record_cls = Community
