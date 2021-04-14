# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import pytest


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture."""
    return {}

@pytest.fixture(scope='module')
def app_config(app_config):
    """Override pytest-invenio app_config fixture."""
    app_config['RECORDS_REFRESOLVER_CLS'] = \
        "invenio_records.resolver.InvenioRefResolver"
    app_config['RECORDS_REFRESOLVER_STORE'] = \
        "invenio_jsonschemas.proxies.current_refresolver_store"

    return app_config
