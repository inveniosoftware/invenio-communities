# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio communities extension."""

from __future__ import absolute_import, print_function

from invenio_indexer.signals import before_record_index
from werkzeug.utils import cached_property

from . import config
from .utils import LazyPIDConverter


class InvenioCommunities(object):
    """Invenio extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    @cached_property
    def community_cls(self):
        """Base community API class."""
        # TODO: Refactor
        from .api import CommunityBase
        from .records.api import CommunityRecordsMixin
        return type(
            'Community',
            (CommunityBase, CommunityRecordsMixin),
            {},
        )

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-communities'] = self

        # TODO: Remove when merged in invenio-records-rest
        app.url_map.converters['lazy_pid'] = LazyPIDConverter

        # TODO: Make configurable or move into separate extension in ".records"
        from invenio_communities.records.indexer import record_indexer_receiver
        before_record_index.dynamic_connect(
            record_indexer_receiver, sender=app, weak=False,
            index=app.config.get(
                'COMMUNITIES_RECORD_INDEX', 'records-record-v1.0.0'),
        )

        @app.context_processor
        def record_context_processors():
            """Jinja context processors for communities record integration."""
            def record_communities(record):
                from invenio_communities.records.api import RecordCommunitiesCollection, Record
                return RecordCommunitiesCollection(Record(record, model=record.model))
            return dict(record_communities=record_communities)


    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        for k in dir(config):
            if k.startswith('COMMUNITIES_'):
                if k == 'COMMUNITIES_REST_ENDPOINTS':
                    # Make sure of registration process.
                    app.config['RECORDS_REST_ENDPOINTS'].update(getattr(
                        config, k))
                app.config.setdefault(k, getattr(config, k))
                if k == 'COMMUNITIES_REST_FACETS':
                    # TODO Might be overriden depending on which package is
                    # initialised first
                    app.config['RECORDS_REST_FACETS'].update(
                        getattr(config, k))
        app.config.setdefault(
            'SUPPORT_EMAIL', getattr(config, 'SUPPORT_EMAIL'))
