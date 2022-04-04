/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import { ManagerMembersResultItem } from "./ManagerMembersResultItem";
import { MembersSearchBarElement } from "../../components/MembersSearchBarElement";
import { MembersResults } from "../components/MembersResult";
import { MembersResultsGridItem } from "../components/MembersResultsGridItem";
import { MembersSearchLayout } from "../components/MembersSearchLayout";
import { ManagerMembersResultsContainer } from "./ManagerMembersResultContainer";
import { parametrize } from "react-overridable";
import { MembersSearchAppContext as MembersSearchAppContextCmp } from "./MembersSearchAppContext";
import { memberVisibilityTypes } from "../";

const domContainer = document.getElementById("community-members-search-root");
const communitiesRoles = JSON.parse(domContainer.dataset.communitiesRoles);
const community = JSON.parse(domContainer.dataset.community);
const permissions = JSON.parse(domContainer.dataset.permissions);

const ManagerMembersResultItemWithConfig = parametrize(
  ManagerMembersResultItem,
  {
    config: {
      roles: communitiesRoles,
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
      roles: communitiesRoles,
      visibility: memberVisibilityTypes,
      permissions: permissions,
    },
  }
);

const MembersSearchAppContext = parametrize(MembersSearchAppContextCmp, {
  community: community,
});

const defaultComponents = {
  "ResultsList.item": ManagerMembersResultItemWithConfig,
  "ResultsGrid.item": MembersResultsGridItem,
  "SearchApp.layout": MembersSearchLayout,
  "SearchBar.element": MembersSearchBarElement,
  "SearchApp.results": MembersResults,
  "ResultsList.container": ManagerMembersResultContainerWithCommunity,
};

// Auto-initialize search app
createSearchAppInit(
  defaultComponents,
  true,
  "invenio-search-config",
  false,
  MembersSearchAppContext
);
