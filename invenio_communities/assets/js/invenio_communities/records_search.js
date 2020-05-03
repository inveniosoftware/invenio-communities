import { SearchWrapper } from "./search_records/SearchMain";
import ReactDOM from "react-dom";
import React from "react";
import { Card, Item, Button } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import axios from "axios";

export function ResultsItemTemplate(record, index) {
  return (
    <Item key={index} href={`/records/${record.id}`}>
      <Item.Content>
        <Item.Header>{record.metadata.titles[0].title}</Item.Header>
        <Item.Description>
          {_truncate(record.metadata.descriptions[0].description, {
            length: 200,
          })}
        </Item.Description>
      </Item.Content>
    </Item>
  );
}

export function ResultsGridItemTemplate(record, index) {
  return (
    <Card fluid key={index} href={`/records/${record.id}`}>
      <Card.Content>
        <Card.Header>{record.metadata.titles[0].title}</Card.Header>
        <Card.Description>
          {_truncate(record.metadata.descriptions[0].description, {
            length: 200,
          })}
        </Card.Description>
      </Card.Content>
    </Card>
  );
}

const aggregations = [
  {
    title: "Access Right",
    agg: {
      field: "access_right",
      aggName: "access_right",
    },
  },
  {
    title: "Resource types",
    agg: {
      field: "resource_type",
      aggName: "resource_type",
    },
  },
];

const sortValues = [
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
];

const resultsPerPageValues = [
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
];


const domContainer = document.getElementById("communities-records-search");
const COMMUNITY_ID = domContainer.dataset.communityId;

const searchApi = {
  axios: {
    baseURL: "",
    url: `/api/records?q=_communities.accepted.id:"${COMMUNITY_ID}"`,
    timeout: 5000,
  },
};

const searchConfig = {
  searchApi,
  aggregations,
  sortValues,
  resultsPerPageValues,
};


ReactDOM.render(
  <SearchWrapper
    ResultsListItem={ResultsItemTemplate}
    ResultsGridItem={ResultsGridItemTemplate}
    searchConfig={searchConfig}
  />,
  domContainer,
);
