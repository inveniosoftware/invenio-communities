// This file is part of Invenio-RDM
// Copyright (C) 2024 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { Component } from "react";
import { OverridableContext } from "react-overridable";
import { InvenioSearchApi, ReactSearchKit, SearchBar, buildUID } from "react-searchkit";
import { Button, Grid } from "semantic-ui-react";
import PropTypes from "prop-types";
import {
  SearchConfigurationContext,
  SearchAppFacets,
  SearchAppResultsPane,
} from "@js/invenio_search_ui/components";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { CommunitiesStatusFilter } from "./CommunitiesStatusFilter";

export class CommunitySelectionSearch extends Component {
  constructor(props) {
    super(props);
    const {
      apiConfigs: { allCommunities },
    } = this.props;

    this.state = {
      selectedConfig: allCommunities,
      sidebarVisible: false,
    };
  }

  /**
   * Namespaces each component object with the specified appID.
   * This is needed since the `CommunitySelectionSearch` component
   * uses two search applications with distinct configs (e.g. to search in "All" or "My" communities)
   */
  prefixAppID(components, appID) {
    // iterate components and prefix them with ".appID"
    return Object.fromEntries(
      Object.entries(components).map(([key, value]) => [`${appID}.${key}`, value])
    );
  }

  render() {
    const {
      selectedConfig: {
        searchApi: selectedSearchApi,
        appId: selectedAppId,
        initialQueryState: selectedInitialQueryState,
        toggleText,
      },
      sidebarVisible,
    } = this.state;

    const {
      apiConfigs: { allCommunities, myCommunities },
      autofocus,
      communitiesStatusFilterEnabled,
      config,
      overriddenComponents,
    } = this.props;

    const searchApi = new InvenioSearchApi(selectedSearchApi);

    const validatedComponents = this.prefixAppID(overriddenComponents, selectedAppId);

    const layoutOptions = {
      listView: true,
      gridView: false,
    };

    const context = {
      selectedAppId,
      buildUID: (element) => buildUID(element, "", selectedAppId),
      ...config,
    };

    return (
      <OverridableContext.Provider value={validatedComponents}>
        <SearchConfigurationContext.Provider value={context}>
          <ReactSearchKit
            appName={selectedAppId}
            urlHandlerApi={{ enabled: false }}
            searchApi={searchApi}
            key={selectedAppId}
            initialQueryState={selectedInitialQueryState}
            defaultSortingOnEmptyQueryString={{ sortBy: "bestmatch" }}
          >
            <Grid padded>
              <Grid.Row>
                {/* Start burger menu for mobile and tablet only */}
                <Grid.Column only="mobile tablet" mobile={4} tablet={1}>
                  <Button
                    basic
                    size="medium"
                    icon="sliders"
                    onClick={() => this.setState({ sidebarVisible: true })}
                    aria-label={i18next.t("Filter results")}
                    className="rel-mb-1"
                  />
                  {/* End burger menu */}
                </Grid.Column>
                {config.aggs && <Grid.Column computer={4} />}
                {communitiesStatusFilterEnabled && (
                  <Grid.Column
                    mobile={8}
                    tablet={4}
                    computer={4}
                    floated="right"
                    className="text-align-right-mobile"
                  >
                    <CommunitiesStatusFilter
                      myCommunitiesOnClick={() => {
                        this.setState({
                          selectedConfig: myCommunities,
                        });
                      }}
                      allCommunitiesOnClick={() => {
                        this.setState({
                          selectedConfig: allCommunities,
                        });
                      }}
                      appID={selectedAppId}
                      allCommunitiesSelected={selectedAppId === allCommunities.appId}
                    />
                  </Grid.Column>
                )}
                <Grid.Column
                  mobile={16}
                  tablet={11}
                  computer={communitiesStatusFilterEnabled ? 8 : 12}
                  verticalAlign="middle"
                  floated="right"
                >
                  <SearchBar
                    placeholder={toggleText}
                    autofocus={autofocus}
                    actionProps={{
                      "icon": "search",
                      "content": null,
                      "className": "search",
                      "aria-label": i18next.t("Search"),
                    }}
                    className="middle aligned"
                  />
                </Grid.Column>
              </Grid.Row>

              <Grid.Row className="community-list-results pt-2">
                <GridResponsiveSidebarColumn
                  width={4}
                  open={sidebarVisible}
                  onHideClick={() => this.setState({ sidebarVisible: false })}
                >
                  <SearchAppFacets aggs={config.aggs} appName={selectedAppId} />
                </GridResponsiveSidebarColumn>
                <Grid.Column mobile={16} tablet={16} computer={12}>
                  <SearchAppResultsPane
                    appName={selectedAppId}
                    layoutOptions={layoutOptions}
                  />
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </ReactSearchKit>
        </SearchConfigurationContext.Provider>
      </OverridableContext.Provider>
    );
  }
}

CommunitySelectionSearch.propTypes = {
  apiConfigs: PropTypes.shape({
    allCommunities: PropTypes.shape({
      appId: PropTypes.string.isRequired,
      initialQueryState: PropTypes.object.isRequired,
      searchApi: PropTypes.object.isRequired,
    }),
    myCommunities: PropTypes.shape({
      appId: PropTypes.string.isRequired,
      initialQueryState: PropTypes.object.isRequired,
      searchApi: PropTypes.object.isRequired,
    }),
  }),
  autofocus: PropTypes.bool,
  overriddenComponents: PropTypes.object,
  config: PropTypes.object.isRequired,
  communitiesStatusFilterEnabled: PropTypes.bool,
};

CommunitySelectionSearch.defaultProps = {
  autofocus: true,
  apiConfigs: {
    allCommunities: {
      initialQueryState: { size: 5, page: 1, sortBy: "bestmatch" },
      searchApi: {
        axios: {
          url: "/api/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.AllCommunities",
      toggleText: "Search in all communities",
    },
    myCommunities: {
      initialQueryState: { size: 5, page: 1, sortBy: "bestmatch" },
      searchApi: {
        axios: {
          url: "/api/user/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.MyCommunities",
      toggleText: "Search in my communities",
    },
  },
  overriddenComponents: {},
  communitiesStatusFilterEnabled: true,
};
