# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schemas for marshmallow."""

from __future__ import absolute_import, print_function

from .json import CommunitySchemaMetadataV1, CommunitySchemaV1

__all__ = ('CommunitySchemaV1', 'CommunitySchemaMetadataV1')
