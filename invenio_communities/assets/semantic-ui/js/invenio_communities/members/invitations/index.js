/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { InvitationsContextProvider as ContextProvider } from "../../api/invitations/InvitationsContextProvider";
import React from "react";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { parametrize } from "react-overridable";
import { InvitationsResults } from "./InvitationsResults";
import { InvitationsSearchBarElement } from "./InvitationsSearchBarElement";
import { InvitationsSearchLayout } from "./InvitationsSearchLayout";
import { InvitationsResultsContainer } from "./InvitationsResultsContainer";
import { InvitationResultItem } from "./InvitationResultItem";

const domContainer = document.getElementById(
  "community-invitations-search-root"
);
const communitiesRoles = JSON.parse(domContainer.dataset.communitiesRoles);
const community = JSON.parse(domContainer.dataset.community);
const permissions = JSON.parse(domContainer.dataset.permissions);

const communityAllowGroupInvites = JSON.parse(
  domContainer.dataset.communityAllowGroupInvites
);

const InvitationResultItemWithConfig = parametrize(InvitationResultItem, {
  config: { roles: communitiesRoles },
  community: community,
});

const InvitationsSearchLayoutWithConfig = parametrize(InvitationsSearchLayout, {
  roles: communitiesRoles,
  community: community,
  permissions: permissions,
  communityAllowGroupInvites: communityAllowGroupInvites,
});

const InvitationsContextProvider = parametrize(ContextProvider, {
  community: community,
});

const defaultComponents = {
  "ResultsList.item": InvitationResultItemWithConfig,
  "SearchApp.layout": InvitationsSearchLayoutWithConfig,
  "SearchBar.element": InvitationsSearchBarElement,
  "SearchApp.results": InvitationsResults,
  "ResultsList.container": InvitationsResultsContainer,
};

// Auto-initialize search app
createSearchAppInit(
  defaultComponents,
  true,
  "invenio-search-config",
  false,
  InvitationsContextProvider
);
