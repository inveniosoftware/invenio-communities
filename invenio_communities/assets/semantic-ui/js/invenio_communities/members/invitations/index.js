/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import { parametrize } from "react-overridable";
import { InvitationResultItemControlled } from "./InvitationResultItemControlled";
import { InvitationsResults } from "./InvitationsResults";
import { InvitationsResultsContainer } from "./InvitationsResultsContainer";
import { InvitationsSearchBarElement } from "./InvitationsSearchBarElement";
import { InvitationsSearchLayout } from "./InvitationsSearchLayout";

const domContainer = document.getElementById(
  "community-invitations-search-root"
);
const communitiesRoles = JSON.parse(domContainer.dataset.communitiesRoles);

const InvitationResultItemControlledWithConfig = parametrize(
  InvitationResultItemControlled,
  {
    config: { roles: communitiesRoles },
  }
);

const defaultComponents = {
  "ResultsList.item": InvitationResultItemControlledWithConfig,
  "SearchApp.layout": InvitationsSearchLayout,
  "SearchBar.element": InvitationsSearchBarElement,
  "SearchApp.results": InvitationsResults,
  "ResultsList.container": InvitationsResultsContainer,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
