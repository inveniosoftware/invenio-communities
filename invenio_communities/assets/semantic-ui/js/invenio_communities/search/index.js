// This file is part of Invenio
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it under the
// terms of the MIT License; see LICENSE file for more details.


import $ from "jquery";
import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  CommunityBucketAggregationElement,
  CommunityRecordFacets,
  CommunityRecordFacetsValues,
  CommunityRecordResultsGridItem,
  CommunityRecordResultsListItem,
  CommunityRecordSearchBarContainer,
  CommunityRecordSearchBarElement,
  CommunityCountComponent,
  CommunityEmptyResults,
  CommunityErrorComponent,
} from "./components";

const initSearchApp = createSearchAppInit({
  "BucketAggregation.element": CommunityBucketAggregationElement,
  "BucketAggregationValues.element": CommunityRecordFacetsValues,
  "ResultsGrid.item": CommunityRecordResultsGridItem,
  "EmptyResults.element": CommunityEmptyResults,
  "ResultsList.item": CommunityRecordResultsListItem,
  "SearchApp.facets": CommunityRecordFacets,
  "SearchApp.searchbarContainer": CommunityRecordSearchBarContainer,
  "SearchBar.element": CommunityRecordSearchBarElement,
  "Count.element": CommunityCountComponent,
  "Error.element": CommunityErrorComponent,
});
