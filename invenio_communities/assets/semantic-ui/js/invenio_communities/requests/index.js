/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { parametrize } from "react-overridable";
import {
  BucketAggregationElement,
  RecordFacetsValues,
  RecordSearchBarElement,
  RequestsEmptyResultsWithState,
  RequestsFacets,
  RequestsResults,
  RequestsResultsGridItemTemplate,
  RequestsResultsItemTemplate,
  RequestsSearchLayout,
} from "./requests";

const domContainer = document.getElementById("communities-request-search-root");

const community = JSON.parse(domContainer.dataset.community);

const RequestsResultsGridItemTemplateWithCommunity = parametrize(
  RequestsResultsGridItemTemplate,
  {
    community: community,
  }
);

const RequestsResultsItemTemplateWithCommunity = parametrize(
  RequestsResultsItemTemplate,
  {
    community: community,
  }
);

const defaultComponents = {
  "BucketAggregation.element": BucketAggregationElement,
  "BucketAggregationValues.element": RecordFacetsValues,
  "SearchApp.facets": RequestsFacets,
  "ResultsList.item": RequestsResultsItemTemplateWithCommunity,
  "ResultsGrid.item": RequestsResultsGridItemTemplateWithCommunity,
  "SearchApp.layout": RequestsSearchLayout,
  "SearchApp.results": RequestsResults,
  "SearchBar.element": RecordSearchBarElement,
  "EmptyResults.element": RequestsEmptyResultsWithState,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
