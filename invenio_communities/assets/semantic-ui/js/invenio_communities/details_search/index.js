// This file is part of Invenio
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it under the
// terms of the MIT License; see LICENSE file for more details.

import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  CommunityCountComponent,
  CommunityEmptyResults,
  CommunityErrorComponent,
  CommunityRecordResultsGridItem,
  CommunityRecordResultsListItem,
  CommunityRecordSearchAppLayout,
  CommunityRecordSearchBarElement,
  CommunityToggleComponent,
} from "./components";
import { parametrize } from "react-overridable";
import {
  ContribSearchAppFacets,
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
} from "@js/invenio_search_ui/components";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  toogle: true,
});

createSearchAppInit({
  "BucketAggregation.element": ContribBucketAggregationElement,
  "BucketAggregationValues.element": ContribBucketAggregationValuesElement,
  "ResultsGrid.item": CommunityRecordResultsGridItem,
  "EmptyResults.element": CommunityEmptyResults,
  "ResultsList.item": CommunityRecordResultsListItem,
  "SearchApp.facets": ContribSearchAppFacetsWithConfig,
  "SearchApp.layout": CommunityRecordSearchAppLayout,
  "SearchBar.element": CommunityRecordSearchBarElement,
  "Count.element": CommunityCountComponent,
  "Error.element": CommunityErrorComponent,
  "SearchFilters.Toggle.element": CommunityToggleComponent,
});
