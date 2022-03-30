/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import { ManagerMemberViewResultItem } from "./ManagerMembersResultItem";
import { MembersSearchBarElement } from "../../components/MembersSearchBarElement";
import { MembersResults } from "../components/MembersResult";
import { MembersResultsGridItem } from "../components/MembersResultsGridItem";
import { MembersSearchLayout } from "../components/MembersSearchLayout";
import { ManagerMembersResultsContainer } from "./ManagerMembersResultContainer";
import { parametrize } from "react-overridable";
import SearchResultsBulkActionsManager from "../../components/bulk_actions/SearchResultsBulkActionsManager"

const domContainer = document.getElementById("community-members-search-root");
const communitiesRoles = JSON.parse(domContainer.dataset.communitiesRoles);

const ManagerMembersResultItemWithConfig = parametrize(
  ManagerMemberViewResultItem,
  {
    config: { roles: communitiesRoles },
  }
);


const defaultComponents = {
  "ResultsList.item": ManagerMembersResultItemWithConfig,
  "ResultsGrid.item": MembersResultsGridItem,
  "SearchApp.layout": MembersSearchLayout,
  "SearchBar.element": MembersSearchBarElement,
  "SearchApp.results": MembersResults,
  "ResultsList.container": ManagerMembersResultsContainer,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents,
  true,
  "invenio-search-config",
  false, SearchResultsBulkActionsManager);
