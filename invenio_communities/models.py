# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio-Communities database models."""

from __future__ import absolute_import, print_function

import logging
from datetime import datetime, timedelta

from flask import current_app, url_for
from invenio_accounts.models import User
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_records.api import Record
from invenio_records.models import RecordMetadata
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import UUIDType

from .errors import InclusionRequestExistsError, \
    InclusionRequestExpiryTimeError, InclusionRequestMissingError, \
    InclusionRequestObsoleteError

logger = logging.getLogger('invenio-communities')


def default_inclusion_request_time():
    """Return the default expiry date (datetime.datetime).

    :returns: Datetime off-setted by some default time delta.
    :rtype: datetime.datetime
    """
    days_expiry = current_app.config['COMMUNITIES_REQUEST_EXPIRY_TIME']
    return datetime.now() + timedelta(days=days_expiry)


class InclusionRequest(db.Model, Timestamp):
    """Association table for Community and Record models.

    A many-to-many association table for records waiting for community
    acceptance or rejection.
    """

    __tablename__ = 'communities_community_record'

    id_community = db.Column(
        db.String(100),
        db.ForeignKey("communities_community.id"),
        primary_key=True
    )
    """Id of the community to which the record is applying."""

    id_record = db.Column(
        UUIDType,
        db.ForeignKey(RecordMetadata.id),
        primary_key=True
    )
    """Id of the record applying to given community."""

    expiry_date = db.Column(db.DateTime, nullable=False,
                            default=default_inclusion_request_time)
    """Expiry date of the record request."""

    #
    # Relationships
    #
    community = db.relationship('Community', backref='inclusion_requests',
                                foreign_keys=[id_community])
    """Relation to the community to which the inclusion request is made."""

    record = db.relationship(RecordMetadata, backref='inclusion_requests',
                             foreign_keys=[id_record])
    """Relation to the record which is requesting for community inclusion."""

    def get_record(self):
        """Return the API object for the Record."""
        return Record(self.record.json, model=self.record)

    @classmethod
    def create(cls, community, record, expiry_date=None):
        """Create a record inclusion request to a community.

        :param community: Community object.
        :type community: `invenio_communities.models.Community`
        :param record: Record API object.
        :type record: `invenio_records.api.Record`
        :param expiry_date: Time after which the request expires and shouldn't
                            be resolved anymore.
        :type expiry_date: datetime.datetime
        """
        expiry_date = expiry_date or default_inclusion_request_time()
        if expiry_date < datetime.now():
            logger.exception("Expiry date cannot be in the past ({}).".format(
                expiry_date))
            raise InclusionRequestExpiryTimeError(community=community,
                                                  record=record)
        communities_key = current_app.config["COMMUNITIES_RECORD_KEY"]
        if communities_key in record and \
                community.id in record[communities_key]:
            logger.exception("Record {0} already in community '{1}'."
                             .format(record.id, community.id))
            raise InclusionRequestObsoleteError(community=community,
                                                record=record)
        try:
            with db.session.begin_nested():
                obj = cls(id_community=community.id,
                          id_record=record.id,
                          expiry_date=expiry_date)
                db.session.add(obj)
            logger.info("Created inclusion request for record {0} and "
                        "community '{1}'.".format(record.id, community.id))
        except IntegrityError:
            logger.exception("Record {0} already pending for community '{1}'."
                             .format(record.id, community.id))
            raise InclusionRequestExistsError(community=community,
                                              record=record)
        return obj


class Community(db.Model, Timestamp):
    """Represent a community."""

    __tablename__ = 'communities_community'

    id = db.Column(db.String(100), primary_key=True)
    """Id of the community."""

    id_user = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        nullable=False
    )
    """Owner of the community."""

    title = db.Column(db.String(length=255), nullable=False, default='')
    """Title of the community."""

    description = db.Column(db.Text, nullable=False, default='')
    """Short description of community, displayed in portal boxes."""

    page = db.Column(db.Text, nullable=False, default='')
    """Long description of community, displayed on an individual page."""

    curation_policy = db.Column(db.Text(), nullable=False, default='')
    """Community curation policy."""

    last_record_accepted = db.Column(db.DateTime(), nullable=False,
                                     default=datetime(2000, 1, 1, 0, 0, 0))
    """Last record acceptance datetime."""

    logo_ext = db.Column(db.String(length=4), nullable=True, default=None)
    """Extension of the logo."""

    ranking = db.Column(db.Integer, nullable=False, default=0)
    """Ranking of community. Updated by ranking deamon."""

    fixed_points = db.Column(db.Integer, nullable=False, default=0)
    """Points which will be always added to overall score of community."""

    #
    # Relationships
    #
    owner = db.relationship(User, backref='communities',
                            foreign_keys=[id_user])
    """Relation to the owner (User) of the community."""

    pending_requests = db.relationship(InclusionRequest)
    """Requests pending for the acceptance to the community."""

    def __repr__(self):
        """String representation of the community object."""
        return "<Community, ID: {}>".format(self.id)

    @classmethod
    def get(cls, community_id):
        """Get a community."""
        return cls.query.filter_by(id=community_id).one_or_none()

    @property
    def logo_url(self):
        """Get URL to collection logo.

        :returns: Path to community logo.
        :rtype: str
        """
        if self.logo_ext:
            buc = current_app.config['COMMUNITIES_BUCKET_UUID']
            key = "{0}/logo.{1}".format(self.id, self.logo_ext)
            return url_for('invenio_files_rest.object_api',
                           bucket_id=buc, key=key)
        else:
            return None

    def add_record(self, record):
        """Add a record to the community.

        :param record: Record object.
        :type record: `invenio_records.api.Record`
        """
        communities_key = current_app.config["COMMUNITIES_RECORD_KEY"]

        if communities_key in record:
            assert isinstance(record[communities_key], list)
            assert self.id not in record[communities_key]
            record[communities_key] = record[communities_key] + [self.id, ]
        else:
            record[communities_key] = [self.id, ]
        record.commit()

    def remove_record(self, record):
        """Remove an already accepted record from the community.

        :param record: Record object.
        :type record: `invenio_records.api.Record`
        """
        communities_key = current_app.config["COMMUNITIES_RECORD_KEY"]

        if communities_key in record and self.id in record[communities_key]:
            record[communities_key] = [c for c in record[communities_key]
                                       if (c != self.id)]
            record.commit()
            db.session.commit()
            RecordIndexer().index_by_id(record.id)

            logger.info("Removed record {0} from community '{1}'.".format(
                record.id, self.id))
        else:
            logger.info("Record {0} requested for removal was not found in "
                        "community '{1}'.".format(record.id, self.id))

    def accept_record(self, record):
        """Accept a record for inclusion in the community.

        :param record: Record object.
        :type record: `invenio_records.api.Record`
        """
        try:
            cr = InclusionRequest.query.filter_by(
                id_record=record.id,
                id_community=self.id).one()
            self.last_record_accepted = datetime.now()
            db.session.delete(cr)
            self.add_record(record)
            db.session.commit()
            RecordIndexer().index_by_id(record.id)
            logger.info("Accepted record {0} to community '{1}'.".format(
                record.id, self.id))
        except NoResultFound:
            logger.exception("Record {0} is not on community '{1}' "
                             "pending list.".format(record.id, self.id))
            raise InclusionRequestMissingError(community=self,
                                               record=record)

    def reject_record(self, record):
        """Reject a record for inclusion in the community.

        :param record: Record object.
        :type record: `invenio_records.api.Record`
        """
        try:
            cr = InclusionRequest.query.filter_by(
                id_record=record.id,
                id_community=self.id).one()
            db.session.delete(cr)
            db.session.commit()
            logger.info("Rejected record {0} from community '{1}'.".format(
                record.id, self.id))
        except NoResultFound:
            logger.exception("Record {0} is not on community '{1}' "
                             "pending list.".format(record.id, self.id))
            raise InclusionRequestMissingError(community=self,
                                               record=record)

    @classmethod
    def filter_communities(cls, p, so):
        """Search for communities.

        Helper function which takes from database only those communities which
        match search criteria. Uses parameter 'so' to set communities in the
        correct order.

        Parameter 'page' is introduced to restrict results and return only
        slice of them for the current page. If page == 0 function will return
        all communities that match the pattern.
        """
        query = cls.query
        if p:
            query = query.filter(db.or_(
                cls.id.like("%" + p + "%"),
                cls.title.like("%" + p + "%"),
                cls.description.like("%" + p + "%"),
            ))
        if so in current_app.config['COMMUNITIES_SORTING_OPTIONS']:
            order = so == 'title' and db.asc or db.desc
            query = query.order_by(order(getattr(cls, so)))
        else:
            query = query.order_by(db.desc(cls.ranking))
        return query

    @property
    def oaiset_spec(self):
        """Return the OAISet 'spec' name for given community.

        :returns: name of corresponding OAISet ('spec').
        :rtype: str
        """
        return current_app.config['COMMUNITIES_OAI_FORMAT'].format(
                community_id=self.id)

    @property
    def community_url(self):
        """Get provisional URL."""
        return url_for(
            'invenio_communities.detail', community_id=self.id,
            _scheme='https', _external=True)

    @property
    def upload_url(self):
        """Get provisional URL."""
        return 'TODO'

    @property
    def community_provisional_url(self):
        """Get provisional URL."""
        return url_for(
            'invenio_communities.curate', community_id=self.id,
            _scheme='https', _external=True)

    @property
    def oaiset_url(self):
        """Return the OAISet 'spec' name for given community.

        :returns: name of corresponding OAISet ('spec').
        :rtype: str
        """
        return url_for(
            'invenio_oaiserver.response',
            verb='ListRecords',
            metadataPrefix='oai_dc', set=self.oaiset_spec, _scheme='https',
            _external=True)


class FeaturedCommunity(db.Model, Timestamp):
    """Represent a featured community."""

    __tablename__ = 'communities_featured_community'

    id = db.Column(db.Integer, primary_key=True)
    """Id of the featured entry."""

    id_community = db.Column(
        db.String(100),
        db.ForeignKey(Community.id),
        nullable=False,
    )
    """Id of the featured community."""

    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    """Start date of the community featuring."""

    #
    # Relationships
    #
    community = db.relationship(Community,
                                backref="featuredcommunity")
    """Relation to the community."""

    @classmethod
    def get_featured_or_none(cls, start_date=None):
        """Get the latest featured community.

        :param start_date: Date after which the featuring starts
        :returns: Community object or None
        :rtype: `invenio_communities.models.Community` or None
        """
        start_date = start_date or datetime.now()

        comm = cls.query.filter(
            FeaturedCommunity.start_date <= start_date).order_by(
            cls.start_date.desc()).first()
        return comm if comm is None else comm.community


__all__ = (
    'Community',
    'InclusionRequest',
    'FeaturedCommunity',
)
