/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import { parametrize } from "react-overridable";
import {
  DropdownSort,
} from '@js/invenio_communities/members/components/SearchDropdowns';
import { InvitationsContextProvider as ContextProvider } from "../../api/invitations/InvitationsContextProvider";
import { InvitationResultItem } from "./InvitationResultItem";
import { InvitationsResults } from "./InvitationsResults";
import { InvitationsResultsContainer } from "./InvitationsResultsContainer";
import { InvitationsSearchBarElement } from "./InvitationsSearchBarElement";
import { InvitationsSearchLayout } from "./InvitationsSearchLayout";

const dataAttr = document.getElementById(
  "community-invitations-search-root"
).dataset;
const community = JSON.parse(dataAttr.community);
const communitiesAllRoles = JSON.parse(dataAttr.communitiesAllRoles);
const communitiesRolesCanInvite = JSON.parse(
  dataAttr.communitiesRolesCanInvite
);
const permissions = JSON.parse(dataAttr.permissions);

const communityAllowGroupInvites = JSON.parse(
  dataAttr.communityAllowGroupInvites
);

const InvitationResultItemWithConfig = parametrize(InvitationResultItem, {
  config: { rolesCanInvite: communitiesRolesCanInvite },
  community: community,
});

const InvitationsSearchLayoutWithConfig = parametrize(InvitationsSearchLayout, {
  roles: communitiesAllRoles,
  rolesCanInvite: communitiesRolesCanInvite,
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
  "Sort.element": DropdownSort,
};

// Auto-initialize search app
createSearchAppInit(
  defaultComponents,
  true,
  "invenio-search-config",
  false,
  InvitationsContextProvider
);
