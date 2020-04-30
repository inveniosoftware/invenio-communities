import { SearchWrapper } from "./search_curate/SearchMain"
import ReactDOM from "react-dom";
import React from "react";
import { Card, Item } from 'semantic-ui-react';
import _truncate from 'lodash/truncate';

//TODO map the request_id

export function ResultsItemTemplate(record, index) {
  return (
    <Item key={index} href={`/records/${record.id}`}>
      <Item.Content>
        <Item.Header>{record.metadata.titles[0].title}</Item.Header>
        <Item.Description>
          <Button class="ui positive button" onClick={() => HandleRequest(request_id, 'accept')}> Accept</Button>
          <Button class="ui button disabled" data-content="Coming soon." onClick={() => HandleRequest(request_id, 'comment')}> Accept</Button>
          <Button class="ui button" onClick={() => HandleRequest(request_id, 'reject')}> Accept</Button>
        </Item.Description>
      </Item.Content>
    </Item>
  )
};



export function ResultsGridItemTemplate(record, index) {
  return (
    <Card fluid key={index} href={`/records/${record.id}`}>
      <Card.Content>
        <Card.Header>{record.metadata.titles[0].title}</Card.Header>
        <Card.Description>
          {_truncate(record.metadata.descriptions[0].description, { length: 200 })}
        </Card.Description>
      </Card.Content>
    </Card>
  );
}


const aggregations = [
  {
    title: "Types",
    agg: {
      field: "type",
      aggName: "type"
    }
  },
  {
    title: "Domains",
    agg: {
      field: "domain",
      aggName: "domain"
    }
  }
];

const sortValues = [
  {
    text: "Best match",
    sortBy: "bestmatch",
    sortOrder: "desc",
    defaultOnEmptyString: true
  },
  {
    text: "Newest",
    sortBy: "mostrecent",
    sortOrder: "asc",
    default: true
  },
  {
    text: "Oldest",
    sortBy: "mostrecent",
    sortOrder: "desc"
  }
];

const resultsPerPageValues = [
  {
    text: "10",
    value: 10
  },
  {
    text: "20",
    value: 20
  },
  {
    text: "50",
    value: 50
  }
];

//TODO change the Query
const searchApi = {
  baseURL: "",
  url: `/api/records?q=_communities.pending.community_pid:${COMMUNITY_ID}`,
  timeout: 5000
};



export const config = {
  searchApi,
  aggregations,
  sortValues,
  resultsPerPageValues
};


const domContainer = document.getElementById("community-id");
const COMMUNITY_ID = domContainer.dataset.comid
console.log(COMMUNITY_ID)

ReactDOM.render(
<SearchWrapper
ResultsListItem={ResultsItemTemplate}
ResultsGridItem={ResultsGridItemTemplate}
searchConfig={config}
/>, document.getElementById("communities-records-curate"));
