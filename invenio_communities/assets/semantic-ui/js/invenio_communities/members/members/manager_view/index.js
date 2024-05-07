/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import { parametrize, overrideStore } from "react-overridable";
import { DropdownSort } from "@js/invenio_search_ui/components";
import { memberVisibilityTypes } from "../";
import { MembersSearchBarElement } from "../../components/MembersSearchBarElement";
import { MembersResults } from "../components/MembersResult";
import { MembersResultsGridItem } from "../components/MembersResultsGridItem";
import { ManagerSearchLayout } from "./ManagerSearchLayout";
import { ManagerEmptyResults } from "./ManagerEmptyResults";
import { ManagerMembersResultsContainer } from "./ManagerMembersResultContainer";
import { ManagerMembersResultItem } from "./ManagerMembersResultItem";
import { MembersSearchAppContext as MembersSearchAppContextCmp } from "./MembersSearchAppContext";

const dataAttr = document.getElementById("community-members-search-root").dataset;
const communitiesRolesCanUpdate = JSON.parse(dataAttr.communitiesRolesCanUpdate);
const communitiesAllRoles = JSON.parse(dataAttr.communitiesAllRoles);
const community = JSON.parse(dataAttr.community);
const permissions = JSON.parse(dataAttr.permissions);
const groupsEnabled = JSON.parse(dataAttr.groupsEnabled);
const rolesCanInvite = JSON.parse(dataAttr.communitiesRolesCanInvite);
const appName = "InvenioCommunities.ManagerSearch";

const ManagerMembersResultItemWithConfig = parametrize(ManagerMembersResultItem, {
  config: {
    rolesCanUpdate: communitiesRolesCanUpdate,
    visibility: memberVisibilityTypes,
    permissions: permissions,
  },
});

const ManagerMembersResultContainerWithCommunity = parametrize(
  ManagerMembersResultsContainer,
  {
    community: community,
    groupsEnabled: groupsEnabled,
    rolesCanInvite: rolesCanInvite,
    config: {
      roles: communitiesAllRoles,
      visibility: memberVisibilityTypes,
      permissions: permissions,
    },
  }
);

const MembersSearchAppContext = parametrize(MembersSearchAppContextCmp, {
  community: community,
});

const ManagerSearchLayoutWithConfig = parametrize(ManagerSearchLayout, {
  community: community,
  groupsEnabled: groupsEnabled,
  rolesCanInvite: rolesCanInvite,
  permissions: permissions,
  roles: communitiesAllRoles,
  appName: appName,
});

const ManagerEmptyResultsWithCommunity = parametrize(ManagerEmptyResults, {
  community: community,
  groupsEnabled: groupsEnabled,
  rolesCanInvite: rolesCanInvite,
});

const defaultComponents = {
  [`${appName}.EmptyResults.element`]: ManagerEmptyResultsWithCommunity,
  [`${appName}.ResultsList.item`]: ManagerMembersResultItemWithConfig,
  [`${appName}.ResultsGrid.item`]: MembersResultsGridItem,
  [`${appName}.SearchApp.layout`]: ManagerSearchLayoutWithConfig,
  [`${appName}.SearchBar.element`]: MembersSearchBarElement,
  [`${appName}.SearchApp.results`]: MembersResults,
  [`${appName}.ResultsList.container`]: ManagerMembersResultContainerWithCommunity,
  [`${appName}.Sort.element`]: DropdownSort,
};

const overriddenComponents = overrideStore.getAll();

// Auto-initialize search app
createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true,
  MembersSearchAppContext
);
