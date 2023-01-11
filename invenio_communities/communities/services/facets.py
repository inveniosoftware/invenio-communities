# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Facet definitions."""

from invenio_i18n import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet

type = TermsFacet(
    field="metadata.type.id",
    label=_("Type"),
    value_labels={
        "organization": _("Organization"),
        "event": _("Event"),
        "topic": _("Topic"),
        "project": _("Project"),
    },
)

visibility = TermsFacet(
    field="access.visibility",
    label=_("Visibility"),
    value_labels={
        "public": _("Public"),
        "restricted": _("Restricted"),
    },
)

role = TermsFacet(
    field="role",
    label=_("Visibility"),
    value_labels={
        "owner": _("Owner"),
        "reader": _("Reader"),
        "manager": _("Manager"),
        "curator": _("Curator"),
    },
)

visible = TermsFacet(
    field="visible",
    label=_("Visibility"),
    value_labels={
        "hidden": _("Hidden"),
        "restricted": _("Restricted"),
    },
)
