# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community base error."""

from math import ceil

from invenio_i18n import gettext as _


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


class LogoSizeLimitError(CommunityError):
    """The provided logo size exceeds limit."""

    def __init__(self, limit, file_size):
        """Initialise error."""
        super().__init__(
            _(
                "Logo size limit exceeded. Limit: {limit} bytes Given: {file_size} bytes".format(
                    limit=ceil(limit), file_size=ceil(file_size)
                )
            )
        )


class OpenRequestsForCommunityDeletionError(CommunityError):
    """There are open requests related to a specific community and cannot be deleted."""

    def __init__(self, requests):
        """Initialise error."""
        super().__init__(
            _(
                "There are {requests} request(s) open for this community. Please, resolve all of them before deleting this community.".format(
                    requests=requests
                )
            )
        )
