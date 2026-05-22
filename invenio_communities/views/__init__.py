# SPDX-FileCopyrightText: 2016-2024 CERN.
# SPDX-FileCopyrightText: 2022 Northwestern University.
# SPDX-License-Identifier: MIT

"""Community views."""

from .api import (
    blueprint,
    create_communities_api_blueprint,
    create_members_api_bp_from_app,
    create_subcommunities_api_blueprint,
)
from .ui import create_ui_blueprint

__all__ = (
    "blueprint",
    "create_communities_api_blueprint",
    "create_members_api_bp_from_app",
    "create_subcommunities_api_blueprint",
    "create_ui_blueprint",
)
