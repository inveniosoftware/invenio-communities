/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React, { Component } from "react";
import ReactDOM from "react-dom";
import {
  ReactSearchKit,
  InvenioSearchApi,
  SearchBar,
  ResultsList,
  EmptyResults
} from "react-searchkit";

const searchApi = new InvenioSearchApi({
  baseURL: "/api/communities",
  url: "",
  timeout: 5000
});


const CommunityRequestList = hits => {

  if (!hits.length) return <div>No results</div>;
  return (
    <div>
      {hits.map(hit => {
        return (
          <div key={hit.metadata.id}>
            <h3><a href={`/communities/${hit.metadata.id}`}>{hit.metadata.title}</a></h3>
            <div dangerouslySetInnerHTML={{ __html: hit.metadata.description }} />
            <span className="label label-primary">{hit.metadata.type}</span>
          </div>
        );
      })}
    </div>
  );
};

class CommunitySearch extends Component {
  render() {
    return (
      <div className="container">
        <a href="/communities/new" className="pull-right btn btn-success">
          <i className="glyphicon-plus"></i> New community
        </a>
        <ReactSearchKit searchApi={searchApi}>
          <div>
            <SearchBar />
            <ResultsList renderElement={CommunityRequestList} />
          </div>
        </ReactSearchKit>
      </div>
    );
  }
}


// ReactDOM.render(<CommunitySearch />, document.getElementById("app"));

export default CommunitySearch;
