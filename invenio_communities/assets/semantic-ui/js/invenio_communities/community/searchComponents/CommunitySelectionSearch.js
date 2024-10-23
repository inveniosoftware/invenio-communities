// This file is part of Invenio-RDM-Records
// Copyright (C) 2024 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { Component } from "react";
import { OverridableContext } from "react-overridable";
import { InvenioSearchApi, ReactSearchKit, SearchBar, buildUID } from "react-searchkit";
import { Button, Grid, Icon, Menu } from "semantic-ui-react";
import PropTypes from "prop-types";
import {
  SearchConfigurationContext,
  SearchAppFacets,
  SearchAppResultsPane,
} from "@js/invenio_search_ui/components";
import { GridResponsiveSidebarColumn, InvenioPopup } from "react-invenio-forms";

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
      overriddenComponents,
      config,
      userAnonymous,
    } = this.props;

    const searchApi = new InvenioSearchApi(selectedSearchApi);
    console.log(selectedSearchApi);

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
            <Grid className="m-0 pb-0 centered" relaxed padded>
              <Grid.Row className="p-3">
                {/* Start burguer menu for mobile and tablet only */}
                <Grid.Column only="mobile tablet" mobile={3} tablet={1}>
                  <Button
                    basic
                    size="medium"
                    icon="sliders"
                    onClick={() => this.setState({ sidebarVisible: true })}
                    aria-label={i18next.t("Filter results")}
                    className="rel-mb-1"
                  />
                  {/* End burguer menu */}
                </Grid.Column>
                <Grid.Column
                  mobile={13}
                  tablet={4}
                  computer={3}
                  floated="right"
                  className="text-align-right-mobile"
                >
                  <Menu role="tablist" className="theme-primary-menu" compact>
                    <Menu.Item
                      as="button"
                      role="tab"
                      id="all-communities-tab"
                      aria-selected={selectedAppId === allCommunities.appId}
                      aria-controls={allCommunities.appId}
                      name="All"
                      active={selectedAppId === allCommunities.appId}
                      onClick={() =>
                        this.setState({
                          selectedConfig: allCommunities,
                        })
                      }
                    >
                      {i18next.t("All")}
                    </Menu.Item>
                    <Menu.Item
                      as="button"
                      role="tab"
                      id="my-communities-tab"
                      aria-selected={selectedAppId === myCommunities.appId}
                      aria-controls={myCommunities.appId}
                      name="My communities"
                      active={selectedAppId === myCommunities.appId}
                      disabled={userAnonymous}
                      onClick={() =>
                        this.setState({
                          selectedConfig: myCommunities,
                        })
                      }
                    >
                      {i18next.t("My communities")}
                      {userAnonymous && (
                        <InvenioPopup
                          popupId="disabled-my-communities-popup"
                          size="small"
                          trigger={
                            <Icon
                              className="mb-5 ml-5"
                              color="grey"
                              name="question circle outline"
                            />
                          }
                          ariaLabel={i18next.t(
                            "You must be logged in to filter by your communities."
                          )}
                          content={i18next.t(
                            "You must be logged in to filter by your communities."
                          )}
                        />
                      )}
                    </Menu.Item>
                  </Menu>
                </Grid.Column>
                <Grid.Column
                  mobile={16}
                  tablet={11}
                  computer={9}
                  verticalAlign="middle"
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
  userAnonymous: PropTypes.bool,
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
  userAnonymous: true,
};
