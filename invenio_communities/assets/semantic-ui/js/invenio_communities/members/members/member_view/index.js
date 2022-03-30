/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";

import { MembersResultsItem } from "./MembersResultItem";
import { MembersSearchBarElement } from "../../components/MembersSearchBarElement";
import { MembersResults } from "../components/MembersResult";
import { MembersResultsGridItem } from "../components/MembersResultsGridItem";
import { MembersResultsContainer } from "../components/MembersResultContainer";
import { MembersSearchLayout } from "../components/MembersSearchLayout";
import { parametrize } from 'react-overridable';


const domContainer = document.getElementById("community-members-search-root");
const communitiesRoles = JSON.parse(domContainer.dataset.communitiesRoles);

const MembersResultItemWithConfig = parametrize(MembersResultsItem, {
  config: { roles: communitiesRoles },
});

const defaultComponents = {
  "ResultsList.item": MembersResultItemWithConfig,
  "ResultsGrid.item": MembersResultsGridItem,
  "SearchApp.layout": MembersSearchLayout,
  "SearchBar.element": MembersSearchBarElement,
  "SearchApp.results": MembersResults,
  "ResultsList.container": MembersResultsContainer,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
