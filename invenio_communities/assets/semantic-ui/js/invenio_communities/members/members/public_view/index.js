/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  DropdownSort
} from '@js/invenio_communities/members/components/SearchDropdowns';

import { PublicMembersResultsItem } from "./PublicMembersResultItem";
import { MembersSearchBarElement } from "../../components/MembersSearchBarElement";
import { MembersResults } from "../components/MembersResult";
import { MembersResultsGridItem } from "../components/MembersResultsGridItem";
import { PublicMembersResultsContainer } from "./PublicMembersResultContainer";
import { PublicMembersSearchLayout } from "./PublicMembersSearchLayout";
import MembersEmptyResults from "../components/MembersEmptyResults";

const defaultComponents = {
  "ResultsList.item": PublicMembersResultsItem,
  "ResultsGrid.item": MembersResultsGridItem,
  "SearchApp.layout": PublicMembersSearchLayout,
  "SearchBar.element": MembersSearchBarElement,
  "SearchApp.results": MembersResults,
  "ResultsList.container": PublicMembersResultsContainer,
  "EmptyResults.element": MembersEmptyResults,
  "Sort.element": DropdownSort,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
