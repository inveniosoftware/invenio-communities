# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community views."""

from .api import create_communities_api_blueprint
from .ui import create_ui_blueprint

__all__ = (
    'create_communities_api_blueprint',
    'create_ui_blueprint'
)
