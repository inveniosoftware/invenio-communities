# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Facet definitions."""

from flask_babelex import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet

type = TermsFacet(
    field='metadata.type',
    label=_('Type'),
    value_labels={
        'organization': _('Organization'),
        'event': _('Event'),
        'topic': _('Topic'),
        'project': _('Project'),
    }
)

visibility = TermsFacet(
    field='access.visibility',
    label=_('Visibility'),
    value_labels={
        'public': _('Public'),
    }
)