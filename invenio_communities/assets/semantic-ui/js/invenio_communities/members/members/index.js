/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import _truncate from "lodash/truncate";
import { createSearchAppInit } from "@js/invenio_search_ui";

import _upperFirst from "lodash/upperFirst";
import { MembersResultsItem } from "./MembersResultItem";
import { MembersResultsGridItem } from "./MembersResultsGridItem";
import { MembersSearchBarElement } from "../components/MembersSearchBarElement";
import { MembersResults } from "./MembersResult";
import { MembersResultsContainer } from "./MembersResultContainer";
import { MembersSearchLayout } from "./MembersSearchLayout";

const defaultComponents = {
  "ResultsList.item": MembersResultsItem,
  "ResultsGrid.item": MembersResultsGridItem,
  "SearchApp.layout": MembersSearchLayout,
  "SearchBar.element": MembersSearchBarElement,
  "SearchApp.results": MembersResults,
  "ResultsList.container": MembersResultsContainer,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
