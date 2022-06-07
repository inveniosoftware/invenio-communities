"""Example of a record/community model."""

from invenio_db import db
from invenio_records.models import RecordMetadataBase

from invenio_communities.records.records.models import CommunityRelationMixin


class MockRecordMetadata(db.Model, RecordMetadataBase):
    """A baisc record."""

    __tablename__ = "mock_metadata"


class MockRecordCommunity(db.Model, CommunityRelationMixin):
    """Relationship between record and community."""

    __tablename__ = "mock_community"
    __record_model__ = MockRecordMetadata
    # __request_model__ = RequestMetadata


# class RecordRequest(db.Model, ReqestRelationMixin):
#     """Relationship between parent record and a request."""

#     __tablename__ = 'rdm_parents_request'
#     __record_model__ = RDMParentMetadata
#     # __request_model__ = RequestMetadata
