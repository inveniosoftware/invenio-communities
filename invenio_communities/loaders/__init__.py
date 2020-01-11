# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Loaders."""

from __future__ import absolute_import, print_function

from invenio_communities.loaders.marshmallow import marshmallow_loader

from ..marshmallow import CommunitySchemaMetadataV1

#: JSON loader using Marshmallow for data validation.
json_v1 = marshmallow_loader(CommunitySchemaMetadataV1)

__all__ = (
    'json_v1',
)
