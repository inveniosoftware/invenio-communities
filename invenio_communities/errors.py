# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community base error."""

from flask_babelex import gettext as _


class CommunityError(Exception):
    """Base exception for community errors."""


class CommunityFeaturedEntryDoesNotExistError(CommunityError):
    """The provided set spec does not exist."""

    def __init__(self, query_arguments):
        """Initialise error."""
        super().__init__(
            _(
                "A featured community entry with {q} does not exist.".format(
                    q=query_arguments
                )
            )
        )
