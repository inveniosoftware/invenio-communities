import { SearchWrapper } from "./search_curate/SearchMain";
import ReactDOM from "react-dom";
import React, { useState } from "react";
import { Card, Item, Button, Icon } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import axios from "axios";

// TODO (react-searchkit): ResultsItemTemplate should be used as a component
// and not just called as a function. Because of that we cannot use hooks. See
// more in https://github.com/inveniosoftware/react-searchkit/issues/113.

const ResultItem = ({ record }) => {
  const request = record.metadata._communities.pending.find(({ id }) => id === COMMUNITY_ID);
  const [status, setStatus] = useState('pending');

  function handleRequest(action) {
    axios
      .post(
        `/api/communities/${request.comid}/requests/inclusion/${request.request_id}/${action}`
      )
      .then((response) => {
        setStatus(action)
        console.log(response);
      });
  }

  return (
    <Item>
      <Item.Content>
        <Item.Header href={`/records/${record.id}`}>{record.metadata.titles[0].title}</Item.Header>
        <Item.Description>
          <Button
            size="tiny"
            positive
            disabled={status !== 'pending'}
            onClick={() => handleRequest("accept")}
          >
            <Icon name="check"/> Accept
          </Button>
          <Button
            size="tiny"
            negative
            disabled={status !== 'pending'}
            onClick={() => handleRequest("reject")}
          >
            <Icon name="delete" inverted/> Reject
          </Button>
          <Button
            size="tiny"
            disabled
            // onClick={() => handleRequest("comment")}
          >
            <Icon name="comment"/> Comment
          </Button>
        </Item.Description>
        <Item.Extra>
          { status === 'pending' ? null : <span>Record was successfully {status}ed</span>}
        </Item.Extra>
      </Item.Content>
    </Item>
  );
}

const ResultsItemTemplate = (record, index) => (
  <ResultItem key={index} record={record} index={index} />
);

function ResultsGridItemTemplate(record, index) {
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


const domContainer = document.getElementById("community-id");
const COMMUNITY_ID = domContainer.dataset.communityId;

const searchApi = {
  axios: {
    baseURL: "",
    url: `/api/records?q=_communities.pending.id:"${COMMUNITY_ID}"`,
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
  document.getElementById("communities-records-curate")
);
