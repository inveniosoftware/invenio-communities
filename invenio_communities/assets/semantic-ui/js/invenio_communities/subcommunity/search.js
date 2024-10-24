/*
 * This file is part of Invenio.
 * Copyright (C) 2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import ReactDOM from "react-dom";
import {
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
  ContribSearchAppFacets,
  SearchResultsBox,
} from "@js/invenio_search_ui/components";
import { parametrize } from "react-overridable";
import {
  CommunitiesSearchBarElement,
  CommunityItem,
  ResultsGridItemTemplate,
  CommunitySelectionSearch,
} from "../community";

import { Container } from "semantic-ui-react";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  help: false,
});

export const overriddenComponents = {
  [`BucketAggregation.element`]: ContribBucketAggregationElement,
  [`BucketAggregationValues.element`]: ContribBucketAggregationValuesElement,
  [`SearchApp.facets`]: ContribSearchAppFacetsWithConfig,
  [`ResultsList.item`]: CommunityItem,
  [`ResultsGrid.item`]: ResultsGridItemTemplate,
  [`SearchBar.element`]: CommunitiesSearchBarElement,
  [`SearchApp.results`]: SearchResultsBox,
};

const domContainer = document.getElementById("communities-search");
const config = JSON.parse(domContainer.dataset?.invenioSearchConfig);
const userAnonymous = JSON.parse(domContainer.dataset?.userAnonymous);
// eslint-disable-next-line react/no-deprecated
ReactDOM.render(
  <Container>
    <CommunitySelectionSearch
      overriddenComponents={overriddenComponents}
      config={config}
      userAnonymous={userAnonymous}
    />
  </Container>,
  domContainer
);
