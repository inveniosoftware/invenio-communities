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
  DropdownSort
} from '@js/invenio_communities/members/components/SearchDropdowns';
import { memberVisibilityTypes } from "../";
import { MembersSearchBarElement } from "../../components/MembersSearchBarElement";
import { MembersResults } from "../components/MembersResult";
import { MembersResultsGridItem } from "../components/MembersResultsGridItem";
import { MembersSearchLayout } from "../components/MembersSearchLayout";
import { ManagerMembersResultsContainer } from "./ManagerMembersResultContainer";
import { ManagerMembersResultItem } from "./ManagerMembersResultItem";
import { MembersSearchAppContext as MembersSearchAppContextCmp } from "./MembersSearchAppContext";

const dataAttr = document.getElementById(
  "community-members-search-root"
).dataset;
const communitiesRolesCanUpdate = JSON.parse(
  dataAttr.communitiesRolesCanUpdate
);
const communitiesAllRoles = JSON.parse(dataAttr.communitiesAllRoles);
const community = JSON.parse(dataAttr.community);
const permissions = JSON.parse(dataAttr.permissions);

const ManagerMembersResultItemWithConfig = parametrize(
  ManagerMembersResultItem,
  {
    config: {
      rolesCanUpdate: communitiesRolesCanUpdate,
      visibility: memberVisibilityTypes,
      permissions: permissions,
    },
  }
);

const ManagerMembersResultContainerWithCommunity = parametrize(
  ManagerMembersResultsContainer,
  {
    community: community,
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

const MembersSearchLayoutWithConfig = parametrize(MembersSearchLayout, {
  roles: communitiesAllRoles,
});

const defaultComponents = {
  "ResultsList.item": ManagerMembersResultItemWithConfig,
  "ResultsGrid.item": MembersResultsGridItem,
  "SearchApp.layout": MembersSearchLayoutWithConfig,
  "SearchBar.element": MembersSearchBarElement,
  "SearchApp.results": MembersResults,
  "ResultsList.container": ManagerMembersResultContainerWithCommunity,
  "Sort.element": DropdownSort,
};

// Auto-initialize search app
createSearchAppInit(
  defaultComponents,
  true,
  "invenio-search-config",
  false,
  MembersSearchAppContext
);
