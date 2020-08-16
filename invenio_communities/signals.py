# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Proxy definitions."""

from __future__ import absolute_import, print_function

from blinker import Namespace

_signals = Namespace()

community_created = _signals.signal('community_created')
