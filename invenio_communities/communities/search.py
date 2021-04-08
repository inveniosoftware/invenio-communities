# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Search utilities."""

from elasticsearch_dsl import Q


def terms_filter(field):
    """Create a term filter used for aggregations.

    :param field: Field name.
    :returns: Function that returns the Terms query.
    """
    def inner(values):
        return Q('terms', **{field: values})
    return inner
