// This file is part of Invenio
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  SearchAppFacets,
  SearchAppResultsPane,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import _get from "lodash/get";
import _truncate from "lodash/truncate";
import React, { Component, useState } from "react";
import PropTypes from "prop-types";
import {
  BucketAggregation,
  Count,
  Pagination,
  ResultsList,
  ResultsPerPage,
  SearchBar,
  Sort,
  withState,
  buildUID,
} from "react-searchkit";
import {
  Button,
  Card,
  Checkbox,
  Container,
  Grid,
  Header,
  Icon,
  Input,
  Item,
  Label,
  List,
  Segment,
} from "semantic-ui-react";
import { DateTime } from "luxon";
import Overridable from "react-overridable";


const RecordSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    onInputChange,
    executeSearch,
    updateQueryState,
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search");
    const onBtnSearchClick = () => {
      updateQueryState({ filters: [] });
      executeSearch();
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        updateQueryState({ filters: [] });
        executeSearch();
      }
    };
    return (
      <Input
        action={{
          icon: "search",
          onClick: onBtnSearchClick,
          className: "search",
          "aria-label": "Search",
        }}
        fluid
        placeholder={placeholder}
        onChange={(event, { value }) => {
          onInputChange(value);
        }}
        value={queryString}
        onKeyPress={onKeyPress}
      />
    );
  }
);

const RecordFacetsValues = ({
  bucket,
  isSelected,
  onFilterClicked,
  getChildAggCmps,
}) => {
  const childAggCmps = getChildAggCmps(bucket);
  const [isActive, setisActive] = useState(false);
  const hasChildren = childAggCmps && childAggCmps.props.buckets.length > 0;
  const keyField = bucket.key_as_string ? bucket.key_as_string : bucket.key;
  return (
    <List.Item key={bucket.key}>
      <div
        className={`facet-wrapper title ${
          hasChildren ? "" : "facet-subtitle"
        } ${isActive ? "active" : ""}`}
      >
        <List.Content className="facet-count">
          <Label circular id={`${keyField}-count`}>
            {bucket.doc_count}
          </Label>
        </List.Content>
        {hasChildren ? (
          <Button
            className="iconhold"
            icon={`angle ${isActive ? "down" : "right"} icon`}
            onClick={() => setisActive(!isActive)}
            aria-label={`${
              isActive
                ? i18next.t("hide subfacets")
                : i18next.t("show subfacets")
            }`}
          />
        ) : null}
        <Checkbox
          label={bucket.label || keyField}
          id={`${keyField}-facet-checkbox`}
          aria-describedby={`${keyField}-count`}
          value={keyField}
          onClick={() => onFilterClicked(keyField)}
          checked={isSelected}
        />
      </div>
      <div className={`content facet-content ${isActive ? "active" : ""}`}>
        {childAggCmps}
      </div>
    </List.Item>
  );
};

const BucketAggregationElement = ({
  agg,
  title,
  containerCmp,
  updateQueryFilters,
}) => {
  const clearFacets = () => {
    if (containerCmp.props.selectedFilters.length) {
      updateQueryFilters([agg.aggName, ""], containerCmp.props.selectedFilters);
    }
  };

  const hasSelections = () => {
    return !!containerCmp.props.selectedFilters.length;
  };

  return (
    <Card className="borderless facet">
      <Card.Content>
        <Card.Header as="h2">
          {title}
          <Button
            basic
            icon
            size="mini"
            floated="right"
            onClick={clearFacets}
            aria-label={i18next.t("Clear selection")}
            title={i18next.t("Clear selection")}
            disabled={!hasSelections()}
          >
            {i18next.t("Clear")}
          </Button>
        </Card.Header>
      </Card.Content>
      <Card.Content>{containerCmp}</Card.Content>
    </Card>
  );
};

const SearchHelpLinks = () => {
  return (
    <Overridable id={"Search.SearchHelpLinks"}>
      <List>
        <List.Item>
          <a href="/help/search">{i18next.t("Search guide")}</a>
        </List.Item>
      </List>
    </Overridable>
  );
};

const RequestsResults = ({
  sortOptions,
  paginationOptions,
  currentResultsState,
}) => {
  const { total } = currentResultsState.data;
  return (
    total && (
      <Grid>
        <Grid.Row>
          <Grid.Column width={16}>
            <Segment>
              <Grid>
                <Grid.Row
                  verticalAlign="middle"
                  className="small padding-tb-5 highlight-background"
                >
                  <Grid.Column width={4}>
                    <Count
                      label={() => (
                        <>
                          {i18next.t("{{total}} result(s) found", {
                            total: total,
                          })}
                        </>
                      )}
                    />
                  </Grid.Column>
                  <Grid.Column
                    width={12}
                    textAlign="right"
                    className="padding-r-5"
                  >
                    {sortOptions && (
                      <Sort
                        values={sortOptions}
                        label={(cmp) => (
                          <>
                            {i18next.t("Sort by")} {cmp}
                          </>
                        )}
                      />
                    )}
                  </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                  <Grid.Column>
                    <ResultsList />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row verticalAlign="middle">
          <Grid.Column width={4}></Grid.Column>
          <Grid.Column width={8} textAlign="center">
            <Pagination
              options={{
                size: "mini",
                showFirst: false,
                showLast: false,
              }}
            />
          </Grid.Column>
          <Grid.Column textAlign="right" width={4}>
            <ResultsPerPage
              values={paginationOptions.resultsPerPage}
              label={(cmp) => (
                <>
                  {cmp} {i18next.t("results per page")}
                </>
              )}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    )
  );
};

function RequestsResultsGridItemTemplate({ result, index }) {
  return (
    <Card fluid key={index} href={`/me/requests/${result.metadata.id}`}>
      <Card.Content>
        <Card.Header>{result.metadata.title}</Card.Header>
        <Card.Description>
          <div
            dangerouslySetInnerHTML={{ __html: result.metadata.description }}
          />
        </Card.Description>
      </Card.Content>
    </Card>
  );
}

function RequestsResultsItemTemplate({ result, index }) {
  const createdDate = new Date(result.created);
  const timestampToRelativeTime = (timestamp) =>
    DateTime.fromISO(timestamp).setLocale(i18next.language).toRelative();
  const differenceInDays = timestampToRelativeTime(createdDate.toISOString());
  return (
    <Item key={index}>
      <Item.Content>
        <Item.Header>
          {result.type && (
            <span className="mr-5">
              <Label size="large">{result.type}</Label>
            </span>
          )}
          <a href={`/me/requests/${result.id}`}>{result.title}</a>
        </Item.Header>

        <Item.Meta className="mt-10">
          <span className="mr-15">
            {/* TODO: Replace by resolved user */}
            {/* {i18next.t(`opened {{difference}} by {{user}}`, {
              difference: differenceInDays,
              user: result.created_by.user,
            })} */}
            {`opened ${differenceInDays} by you`}
          </span>
          {result.receiver.community && (
            <>
              <Icon className="default-margin" name="users" />
              <span className="ml-5">
                {/* TODO: Replace by resolved receiver */}
                {/* {result.receiver.community} */}
                Biodiversity Literature Repository
              </span>
            </>
          )}
        </Item.Meta>
      </Item.Content>
    </Item>
  );
}

class RequestStatusFilterComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      open: undefined,
    };
  }

  componentDidMount() {
    const { currentQueryState } = this.props;
    const userSelectionFilters = currentQueryState.filters;
    const openFilter = userSelectionFilters.find((obj) =>
      obj.includes("is_open")
    );
    if (openFilter) {
      this.setState({
        open: openFilter.includes("true"),
      });
    }
  }

  /**
   * Updates queryFilters based on selection and removing previous filters
   * @param {string} OpenStatus true if open requests and false if closed requests
   */
  retrieveRequests = (OpenStatus) => {
    const { currentQueryState, updateQueryState } = this.props;
    const { open } = this.state;

    if (open === OpenStatus) {
      return;
    }
    this.setState({
      open: OpenStatus,
    });
    currentQueryState.filters = [];
    currentQueryState.filters.push(["is_open", OpenStatus]);
    updateQueryState(currentQueryState);
  };

  retrieveOpenRequests = () => {
    this.retrieveRequests(true);
  };

  retrieveClosedRequests = () => {
    this.retrieveRequests(false);
  };

  render() {
    const { open } = this.state;
    return (
      <Button.Group basic>
        <Button
          className="request-search-filter"
          onClick={this.retrieveOpenRequests}
          active={open === true}
        >
          {i18next.t("Open")}
        </Button>
        <Button
          className="request-search-filter"
          onClick={this.retrieveClosedRequests}
          active={open === false}
        >
          {i18next.t("Closed")}
        </Button>
      </Button.Group>
    );
  }
}

RequestStatusFilterComponent.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
};

const RequestStatusFilter = withState(RequestStatusFilterComponent);

const RequestsSearchLayout = (props) => {
  return (
    <Container>
      <Grid>
        <Grid.Row columns={3}>
          <Grid.Column width={4} />
          <Grid.Column width={3}>
            <RequestStatusFilter />
          </Grid.Column>
          <Grid.Column width={9}>
            <SearchBar placeholder={i18next.t("Search requests...")} />
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column width={4}>
            <SearchAppFacets aggs={props.config.aggs} />
          </Grid.Column>
          <Grid.Column width={12}>
            <SearchAppResultsPane layoutOptions={props.config.layoutOptions} />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Container>
  );
};

const RequestsFacets = ({ aggs, currentResultsState }) => {
  return (
    <aside aria-label={i18next.t("filters")} id="search-filters">
      {aggs.map((agg) => {
        return (
          <div className="ui accordion" key={agg.title}>
            <BucketAggregation title={agg.title} agg={agg} />
          </div>
        );
      })}
      <SearchHelpLinks />
    </aside>
  );
};

const RequestsEmptyResults = (props) => {
  const { queryString, userSelectionFilters } = props;
  const is_open = userSelectionFilters.some(
    (obj) => obj.includes("is_open") && obj.includes("true")
  );
  const filtersToNotReset = userSelectionFilters.find((obj) =>
    obj.includes("is_open")
  );
  const elementsToReset = {
    queryString: "",
    page: 1,
    filters: [filtersToNotReset],
  };

  const AllDone = () => {
    return (
      <>
        <Header as="h1" icon>
          {i18next.t("All done!")}
          <Header.Subheader>
            {i18next.t("You've caught up with all open requests.")}
          </Header.Subheader>
        </Header>
      </>
    );
  };

  const NoResults = () => {
    return (
      <>
        <Header icon>
          <Icon name="search" />
          {i18next.t("No requests found!")}
        </Header>
        {queryString && (
          <Button
            primary
            onClick={() => props.updateQueryState(elementsToReset)}
          >
            {i18next.t("Reset search")}
          </Button>
        )}
      </>
    );
  };

  const allRequestsDone = is_open && !queryString;
  return (
    <>
      <Segment placeholder textAlign="center">
        {allRequestsDone ? <AllDone /> : <NoResults />}
      </Segment>
    </>
  );
};

const RequestsEmptyResultsWithState = withState(
  RequestsEmptyResults
);

export const defaultComponents = (appId) => {
  return {
    [buildUID('BucketAggregation.element', '', appId)]: BucketAggregationElement,
    [buildUID('BucketAggregationValues.element', '', appId)]: RecordFacetsValues,
    [buildUID('SearchApp.facets', '', appId)]: RequestsFacets,
    [buildUID('ResultsList.item', '', appId)]: RequestsResultsItemTemplate,
    [buildUID('ResultsGrid.item', '', appId)]: RequestsResultsGridItemTemplate,
    [buildUID('SearchApp.layout', '', appId)]: RequestsSearchLayout,
    [buildUID('SearchApp.results', '', appId)]: RequestsResults,
    [buildUID('SearchBar.element', '', appId)]: RecordSearchBarElement,
    [buildUID('EmptyResults.element', '', appId)]: RequestsEmptyResultsWithState,
  }
};
