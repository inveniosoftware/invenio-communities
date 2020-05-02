// This file is part of InvenioRDM
// Copyright (C) 2020 CERN.
// Copyright (C) 2020 Northwestern University.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component, useContext } from "react";

import { Container, Grid } from "semantic-ui-react";
import { ReactSearchKit, InvenioSearchApi } from "react-searchkit";

import { SearchResults } from "./SearchResults";
import { SearchFacets } from "./SearchFacets";
import { SearchBar } from "./SearchBar";

export const SearchMain = () => {
  const { searchConfig } = useContext(SearchComponentsContext);
  var api = new InvenioSearchApi(searchConfig.searchApi)
  return (
    <>
      <ReactSearchKit searchApi={api} eventListenerEnabled={true}>
        <SearchBar />
        <Container>
          <Grid relaxed style={{ padding: "2em 0" }}>
            <Grid.Row columns={2}>
              <Grid.Column width={4} className="search-aggregations">
                <SearchFacets searchConfig={searchConfig} />
              </Grid.Column>
              <Grid.Column width={12}>
                <SearchResults />
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Container>
      </ReactSearchKit>
    </>
  );
};


export const SearchComponentsContext = React.createContext();

export class SearchWrapper extends Component {
  render() {
    const {ResultsListItem, ResultsGridItem, searchConfig} = this.props;
    const contextValue = {
      ResultsListItem,
      ResultsGridItem,
      searchConfig
    }
    return (
      <SearchComponentsContext.Provider value={contextValue}>
        <SearchMain />
      </SearchComponentsContext.Provider>
    );
  }
};
