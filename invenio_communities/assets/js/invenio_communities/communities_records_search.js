import { SearchWrapper } from "./search_records/SearchMain"
import ReactDOM from "react-dom";
import React from "react";
import { Card, Item, Button } from 'semantic-ui-react';
import _truncate from 'lodash/truncate';
import axios from "axios";

export function ResultsItemTemplate(record, index) {
  return (
    <Item key={index} href={`/records/${record.id}`}>
      <Item.Content>
        <Item.Header>{record.metadata.titles[0].title}</Item.Header>
        <Item.Description>
          {_truncate(record.metadata.descriptions[0].description, { length: 200 })}
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

export function HandleRequest(request_id, action) {
  axios.post(`/api/communities/{COMMUNITY_ID}/requests/inclusion/{request_id}/{action}`)
  .then(response => {
    console.log(response);
  })
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


const searchApi = {
  baseURL: "",
  url: `/api/records?q=_communities.pending.community_pid:${COMMUNITY_ID}`,
  timeout: 5000
};


// 1. Community search
// 2. Community records search
// 3. Community curation

// {
//   ...,
//   'communities': {
//     'pending': [
//       {
//         'community_pid': 'biosyslit',
//         'request_id': 'abdef...',
//         'created_by': 1234,
//       }
//     ]
//   }
// }

// 1 - Alex

// 2 - George

// biosyslit

// _exists_:_communities.pending

// A --(1)-> biosyslit (comment, delete)
// B <-(2)-- biosyslit (accept, reject, comment)


// A --(1)-> biosyslit (accept, reject, comment, delete)
// B <-(2)-- biosyslit (accept, reject, comment)


// incoming: 1 in B.owners and request.created_by != 1
// outgoing: request.created_by == 1

// C


export const config = {
  searchApi,
  aggregations,
  sortValues,
  resultsPerPageValues
};


const domContainer = document.getElementById("community-id");
const COMMUNITY_ID = domContainer.dataset.community_id

ReactDOM.render(
<SearchWrapper
ResultsListItem={ResultsItemTemplate}
ResultsGridItem={ResultsGridItemTemplate}
searchConfig={config}
/>, document.getElementById("communities-records-search"));
