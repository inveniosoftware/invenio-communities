import ReactDOM from "react-dom";
import React from "react";
import { Card, Item, Button } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { SearchApp } from "../invenio_search_ui/SearchApp";
import { overrideStore } from "react-overridable";

export function ResultsItemTemplate({result, index}) {
  return (
    <Item key={index} href={`/records/${result.id}`}>
      <Item.Content>
        <Item.Header>{result.metadata.titles[0].title}</Item.Header>
        <Item.Description>
          {_truncate(result.metadata.descriptions[0].description, {
            length: 200,
          })}
        </Item.Description>
      </Item.Content>
    </Item>
  );
}

export function ResultsGridItemTemplate({result, index}) {
  return (
    <Card fluid key={index} href={`/records/${result.id}`}>
      <Card.Content>
        <Card.Header>{result.metadata.titles[0].title}</Card.Header>
        <Card.Description>
          {_truncate(result.metadata.descriptions[0].description, {
            length: 200,
          })}
        </Card.Description>
      </Card.Content>
    </Card>
  );
}

overrideStore.add("ResultsList.item", ResultsItemTemplate);
overrideStore.add("ResultsGrid.item", ResultsGridItemTemplate);

const domContainer = document.getElementById("communities-records-search");
const COMMUNITY_ID = domContainer.dataset.communityId;
const searchConfig = {
  api: `/api/records?q=_communities.accepted.id:"${COMMUNITY_ID}"`,
  mimetype: 'application/json',
  aggs: [
    {
      title: "Access Right",
      field: "access_right",
      aggName: "access_right",
    },
    {
      title: "Resource types",
      field: "resource_type",
      aggName: "resource_type",
    },
  ],
  sort_options:[
    {
      text: "Best match",
      sortBy: "bestmatch",
      sortOrder: "desc",
      defaultOnEmptyString: true,
    },
    {
      text: "Newest",
      sortBy: "mostrecent",
      sortOrder: "asc",
      default: true,
    },
    {
      text: "Oldest",
      sortBy: "mostrecent",
      sortOrder: "desc",
    },
  ],
  resultsPerPageValues: [
    {
      text: "10",
      value: 10,
    },
    {
      text: "20",
      value: 20,
    },
    {
      text: "50",
      value: 50,
    },
  ],
};

ReactDOM.render(
  <SearchApp config={searchConfig} appName={"communities-records-search"}/>,
  document.getElementById("communities-records-search")
);
