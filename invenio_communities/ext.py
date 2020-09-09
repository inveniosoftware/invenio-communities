# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio communities extension."""

from __future__ import absolute_import, print_function

from flask_principal import identity_loaded
from invenio_base.utils import obj_or_import_string
from invenio_indexer.signals import before_record_index
from werkzeug.utils import cached_property

from . import config
from .permission_loaders import load_permissions_on_identity_loaded
from .signals import community_created
from .utils import LazyPIDConverter, obj_or_import_string, set_default_admin


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
        # def default_class_factory():
        #     from .api import CommunityBase
        #     from .records.api import CommunityRecordsMixin
        #     from .members.api import CommunityMembersMixin
        #     return type(
        #         'Community',
        #         (CommunityBase, CommunityRecordsMixin, CommunityMembersMixin),
        #         {},
        #     )
        # return self.app.config['COMMUNITY_CLS'] or default_class_factory()

        from .api import CommunityBase
        from .members.api import CommunityMembersMixin
        from .records.api import CommunityRecordsMixin
        from .records.collections.api import CommunityCollectionsMixin
        return type(
            'Community',
            (CommunityBase, CommunityRecordsMixin,
             CommunityMembersMixin, CommunityCollectionsMixin),
            {},
        )

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-communities'] = self

        # TODO: Remove when merged in invenio-records-rest
        app.url_map.converters['lazy_pid'] = LazyPIDConverter

        @app.context_processor
        def record_context_processors():
            """Jinja context processors for communities record integration."""
            def record_communities_ui_data(record):
                from invenio_communities.records.api import Record, \
                    RecordCommunitiesCollection
                record_commmunities = RecordCommunitiesCollection(
                    Record(record, model=record.model))
                record_communities_dict = record_commmunities.as_dict()
                communities_dict = {
                    record_community.community.pid.pid_value:
                        record_community.community.dumps()
                    for record_community in record_commmunities}
                return {
                    'record_communities': record_communities_dict,
                    'communities': communities_dict
                }
            return dict(record_communities_ui_data=record_communities_ui_data)

        self._register_signals(app)

        identity_loaded.connect_via(app)(
            load_permissions_on_identity_loaded
        )

    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        for k in dir(config):
            if k.startswith('COMMUNITIES_'):
                if k == 'COMMUNITIES_REST_ENDPOINTS':
                    # Make sure of registration process.
                    app.config.setdefault('RECORDS_REST_ENDPOINTS', {})
                    app.config['RECORDS_REST_ENDPOINTS'].update(getattr(
                        config, k))
                app.config.setdefault(k, getattr(config, k))
                if k == 'COMMUNITIES_REST_FACETS':
                    app.config.setdefault('RECORDS_REST_FACETS', {})
                    app.config['RECORDS_REST_FACETS'].update(
                        getattr(config, k))
                if k == 'COMMUNITIES_REST_SORT_OPTIONS':
                    # TODO Might be overriden depending on which package is
                    # initialised first
                    app.config.setdefault('RECORDS_REST_SORT_OPTIONS', {})
                    app.config['RECORDS_REST_SORT_OPTIONS'].update(
                        getattr(config, k))
                if k == 'COMMUNITIES_REST_DEFAULT_SORT':
                    # TODO Might be overriden depending on which package is
                    # initialised first
                    app.config.setdefault('RECORDS_REST_DEFAULT_SORT', {})
                    app.config['RECORDS_REST_DEFAULT_SORT'].update(
                        getattr(config, k))

        app.config.setdefault(
            'SUPPORT_EMAIL', getattr(config, 'SUPPORT_EMAIL'))

    def _register_signals(self, app):
        """Register signals."""
        # TODO: Find easier way to connect to "records*" indexes
        def _index_starts_with(prefix):
            return lambda _, __, **kw: kw.get('index', '').startswith(prefix)
        records_index_prefix = app.config.get(
            'COMMUNITIES_RECORD_INDEX', 'records').split('-', 1)[0]

        # TODO: Make configurable or move into separate extension in ".records"
        from invenio_communities.records.indexer import record_indexer_receiver
        before_record_index.dynamic_connect(
            obj_or_import_string(
                app.config.get('COMMUNITIES_INDEXER_RECEIVER'),
                record_indexer_receiver),
            sender=app,
            weak=False,
            condition_func=_index_starts_with(records_index_prefix),
        )

        # TODO: Make configurable
        from invenio_communities.records.collections.indexer import \
            record_collections_indexer_receiver
        before_record_index.dynamic_connect(
            record_collections_indexer_receiver,
            sender=app,
            weak=False,
            condition_func=_index_starts_with(records_index_prefix),
        )

        community_created.connect(set_default_admin, weak=False)
