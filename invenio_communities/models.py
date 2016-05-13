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

import hashlib
from datetime import datetime

from flask import current_app, url_for
from invenio_accounts.models import User
from invenio_db import db
from invenio_records.api import Record
from invenio_records.models import RecordMetadata
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError, NoResultFound
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import UUIDType

from .errors import CommunitiesError, InclusionRequestExistsError, \
    InclusionRequestExpiryTimeError, InclusionRequestMissingError, \
    InclusionRequestObsoleteError
from .signals import inclusion_request_created
from .utils import save_and_validate_logo


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

    id_user = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        nullable=True,
        default=None
    )
    """User making the request (optional)."""

    expires_at = db.Column(
        db.DateTime,
        nullable=True,
        default=None,
    )
    """Expiry date of the record request."""

    #
    # Relationships
    #
    community = db.relationship(
        'Community', backref='inclusion_requests', foreign_keys=[id_community])
    """Relation to the community to which the inclusion request is made."""

    record = db.relationship(
        RecordMetadata, backref='inclusion_requests', foreign_keys=[id_record])
    """Relation to the record which is requesting for community inclusion."""

    user = db.relationship(
        User, backref='inclusion_requests', foreign_keys=[id_user])
    """Relation to the User making the inclusion request."""

    def get_record(self):
        """Return the API object for the Record."""
        return Record.get_record(self.id_record)

    def delete(self):
        """Delete this request."""
        db.session.delete(self)

    @classmethod
    def create(cls, community, record, user=None, expires_at=None,
               notify=True):
        """Create a record inclusion request to a community.

        :param community: Community object.
        :param record: Record API object.
        :param expires_at: Time after which the request expires and shouldn't
            be resolved anymore.
        """
        if expires_at and expires_at < datetime.utcnow():
            raise InclusionRequestExpiryTimeError(
                community=community, record=record)

        if community.has_record(record):
            raise InclusionRequestObsoleteError(
                community=community, record=record)

        try:
            # Create inclusion request
            with db.session.begin_nested():
                obj = cls(
                    id_community=community.id,
                    id_record=record.id,
                    user=user,
                    expires_at=expires_at
                )
                db.session.add(obj)
        except (IntegrityError, FlushError):
            raise InclusionRequestExistsError(
                community=community, record=record)

        # Send signal
        inclusion_request_created.send(
            current_app._get_current_object(),
            request=obj,
            notify=notify
        )

        return obj

    @classmethod
    def get(cls, community_id, record_uuid):
        """Get an inclusion request."""
        return cls.query.filter_by(
            id_record=record_uuid, id_community=community_id
        ).one()

    @classmethod
    def get_by_record(cls, record_uuid):
        """Get inclusion requests for a given record."""
        return cls.query.filter_by(id_record=record_uuid)


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

    last_record_accepted = db.Column(
        db.DateTime(), nullable=False, default=datetime(2000, 1, 1, 0, 0, 0))
    """Last record acceptance datetime."""

    logo_ext = db.Column(db.String(length=4), nullable=True, default=None)
    """Extension of the logo."""

    ranking = db.Column(db.Integer, nullable=False, default=0)
    """Ranking of community. Updated by ranking deamon."""

    fixed_points = db.Column(db.Integer, nullable=False, default=0)
    """Points which will be always added to overall score of community."""

    deleted_at = db.Column(db.DateTime, nullable=True, default=None)
    """Time at which the community was soft-deleted."""

    #
    # Relationships
    #
    owner = db.relationship(User, backref='communities',
                            foreign_keys=[id_user])
    """Relation to the owner (User) of the community."""

    def __repr__(self):
        """String representation of the community object."""
        return "<Community, ID: {}>".format(self.id)

    @classmethod
    def create(cls, community_id, user_id, **data):
        """Get a community."""
        with db.session.begin_nested():
            obj = cls(id=community_id, id_user=user_id, **data)
            db.session.add(obj)
        return obj

    def save_logo(self, stream, filename):
        """Get a community."""
        logo_ext = save_and_validate_logo(stream, filename, self.id)
        if logo_ext:
            self.logo_ext = logo_ext
            return True
        return False

    @classmethod
    def get(cls, community_id, with_deleted=False):
        """Get a community."""
        q = cls.query.filter_by(id=community_id)
        if not with_deleted:
            q = q.filter(cls.deleted_at.is_(None))
        return q.one_or_none()

    @classmethod
    def get_by_user(cls, user_id, with_deleted=False):
        """Get a community."""
        query = cls.query.filter_by(
            id_user=user_id
        )
        if not with_deleted:
            query = query.filter(cls.deleted_at.is_(None))

        return query.order_by(db.asc(Community.title))

    @classmethod
    def filter_communities(cls, p, so, with_deleted=False):
        """Search for communities.

        Helper function which takes from database only those communities which
        match search criteria. Uses parameter 'so' to set communities in the
        correct order.

        Parameter 'page' is introduced to restrict results and return only
        slice of them for the current page. If page == 0 function will return
        all communities that match the pattern.
        """
        query = cls.query if with_deleted else \
            cls.query.filter(cls.deleted_at.is_(None))

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

    def add_record(self, record):
        """Add a record to the community.

        :param record: Record object.
        :type record: `invenio_records.api.Record`
        """
        key = current_app.config['COMMUNITIES_RECORD_KEY']
        record.setdefault(key, [])

        assert self.id not in record[key]
        record[key].append(self.id)

        if current_app.config["COMMUNITIES_OAI_ENABLED"]:
            from invenio_oaiserver.models import OAISet
            oaiset = OAISet.query.filter_by(spec=self.oaiset_spec).one()
            oaiset.add_record(record)

    def remove_record(self, record):
        """Remove an already accepted record from the community.

        :param record: Record object.
        :type record: `invenio_records.api.Record`
        """
        key = current_app.config['COMMUNITIES_RECORD_KEY']

        assert self.id in record.get(key, [])

        record[key] = [c for c in record[key] if c != self.id]

        if current_app.config["COMMUNITIES_OAI_ENABLED"]:
            from invenio_oaiserver.models import OAISet
            oaiset = OAISet.query.filter_by(spec=self.oaiset_spec).one()
            oaiset.remove_record(record)

    def has_record(self, record):
        """Check if record is in community."""
        return self.id in \
            record.get(current_app.config["COMMUNITIES_RECORD_KEY"], [])

    def accept_record(self, record):
        """Accept a record for inclusion in the community.

        :param record: Record object.
        """
        try:
            with db.session.begin_nested():
                req = InclusionRequest.get(self.id, record.id)
                req.delete()
                self.add_record(record)
                self.last_record_accepted = datetime.utcnow()
        except NoResultFound:
            raise InclusionRequestMissingError(
                community=self, record=record)

    def reject_record(self, record):
        """Reject a record for inclusion in the community.

        :param record: Record object.
        """
        try:
            with db.session.begin_nested():
                req = InclusionRequest.get(self.id, record.id)
                req.delete()
        except NoResultFound:
            raise InclusionRequestMissingError(
                community=self, record=record)

    def delete(self):
        """Mark the community for deletion.

        :param delete_time: DateTime after which to delete the community.
        :type delete_time: datetime.datetime
        :raises: CommunitiesError
        """
        if self.deleted_at is not None:
            raise CommunitiesError(community=self)
        else:
            self.deleted_at = datetime.utcnow()

    def undelete(self):
        """Remove the community marking for deletion."""
        if self.deleted_at is None:
            raise CommunitiesError(community=self)
        else:
            self.deleted_at = None

    @property
    def is_deleted(self):
        """Return whether given community is marked for deletion."""
        return self.deleted_at is not None

    @property
    def logo_url(self):
        """Get URL to collection logo.

        :returns: Path to community logo.
        :rtype: str
        """
        if self.logo_ext:
            buc = current_app.config['COMMUNITIES_BUCKET_UUID']
            key = "{0}/logo.{1}".format(self.id, self.logo_ext)
            return url_for(
                'invenio_files_rest.object_api', bucket_id=buc, key=key)
        else:
            return None

    @property
    def community_url(self):
        """Get provisional URL."""
        return url_for(
            'invenio_communities.detail', community_id=self.id, _external=True)

    @property
    def community_provisional_url(self):
        """Get provisional URL."""
        return url_for(
            'invenio_communities.curate', community_id=self.id, _external=True)

    @property
    def upload_url(self):
        """Get provisional URL."""
        return 'TODO'

    @property
    def oaiset_spec(self):
        """Return the OAISet 'spec' name for given community.

        :returns: name of corresponding OAISet ('spec').
        :rtype: str
        """
        return current_app.config['COMMUNITIES_OAI_FORMAT'].format(
                community_id=self.id)

    @property
    def oaiset_url(self):
        """Return the OAISet 'spec' name for given community.

        :returns: name of corresponding OAISet ('spec').
        :rtype: str
        """
        return url_for(
            'invenio_oaiserver.response',
            verb='ListRecords',
            metadataPrefix='oai_dc', set=self.oaiset_spec, _external=True)

    @property
    def version_id(self):
        """Return the version of the community.

        :returns: hash which encodes the community id and its las update.
        :rtype: str
        """
        return hashlib.sha1('{0}__{1}'.format(
            self.id, self.updated).encode('utf-8')).hexdigest()


class FeaturedCommunity(db.Model, Timestamp):
    """Represent a featured community."""

    __tablename__ = 'communities_featured_community'

    id = db.Column(db.Integer, primary_key=True)
    """Id of the featured entry."""

    id_community = db.Column(
        db.String(100), db.ForeignKey(Community.id), nullable=False)
    """Id of the featured community."""

    start_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    """Start date of the community featuring."""

    #
    # Relationships
    #
    community = db.relationship(Community, backref="featuredcommunity")
    """Relation to the community."""

    @classmethod
    def get_featured_or_none(cls, start_date=None):
        """Get the latest featured community.

        :param start_date: Date after which the featuring starts
        :returns: Community object or None
        :rtype: `invenio_communities.models.Community` or None
        """
        start_date = start_date or datetime.utcnow()

        comm = cls.query.filter(
            FeaturedCommunity.start_date <= start_date
        ).order_by(
            cls.start_date.desc()
        ).first()
        return comm if comm is None else comm.community
