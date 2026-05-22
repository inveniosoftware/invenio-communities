# SPDX-FileCopyrightText: 2022-2024 CERN.
# SPDX-FileCopyrightText: 2023 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Facet definitions."""

from invenio_i18n import lazy_gettext as _
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
