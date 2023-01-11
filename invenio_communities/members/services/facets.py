# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Facets for the members search."""

from invenio_i18n import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet

from ...proxies import current_roles

role = TermsFacet(
    field="role",
    label=_("Role"),
    value_labels=lambda keys: {k: current_roles[k].title for k in keys},
)

status = TermsFacet(
    field="request.status",
    label=_("Status"),
    value_labels={
        "submitted": _("Submitted"),
        "expired": _("Expired"),
        "accepted": _("Accepted"),
        "declined": _("Declined"),
        "cancelled": _("Cancelled"),
    },
)

visibility = TermsFacet(
    field="visible",
    label=_("Visibility"),
    value_labels={"true": _("Public"), "false": _("Hidden")},
)

is_open = TermsFacet(
    field="request.is_open",
    label=_("Status"),
    value_labels={"true": _("Open"), "false": _("Closed")},
)
