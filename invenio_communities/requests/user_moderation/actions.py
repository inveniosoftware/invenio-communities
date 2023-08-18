# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Communities user moderation actions."""


def on_block(user_id, uow=None, **kwargs):
    """Removes communities that belong to a user."""
    pass


def on_restore(user_id, uow=None, **kwargs):
    """Restores communities that belong to a user."""
    pass
