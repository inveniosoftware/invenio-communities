/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import {
  ResultsList,
} from "react-searchkit";

// /communities/<comid>/requests/inclusion
var community_id = window.location.pathname.split('/')[2];


var listInclusionRequests = (commID, successHandler, errorHandler) => {
  axios
  .get(`/api/communities/${commID}/requests/inclusion`)
  .then(function (response) {
    successHandler(response.data);
    // debugger;
  })
  .catch(error => {
    errorHandler(error.response.data)
  })
}


const CommunityCuration = (communityID) => {

  const [inclusionRequests, setInclusionRequests] = useState(false);
  const [errors, setErrors] = useState(false);


  return (
    <div className="container">
      <h1>Inclusion requests</h1>
      <button type="button" onClick={() => listInclusionRequests(community_id, setInclusionRequests, setErrors)}>List Inclusion Requests</button>
      {inclusionRequests ? (
        <table className="ui compact celled definition table">
          <thead>
            <tr>
              <th>Record Description</th>
              <th>Record PID</th>
              <th>User requesting</th>
              <th>Comments</th>
              <th>Request ID</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Description of the record...</td>
              <td>{inclusionRequests.results[0].record_pid}</td>
              <td>John</td>
              <td>{inclusionRequests.results[0].comments[0].message}</td>
              <td>{inclusionRequests.results[0].request_id}</td>
              <td>
                <button type="button">Accept</button>
                <button type="button">Reject</button>
              </td>
            </tr>
            </tbody>
        </table>

        // <table>
        //   {inclusionRequests.map(ir => {
        //     return (
        //     <tr>{ir}</tr>
        //       <tr>
        //         <td>{ir.request_id}</td>
        //         <td>{ir.record_pid}</td>
        //         <td>{ir.messages}</td>
        //       </tr>
        //     )
        //   })}
        // </table>
      ) : (
        <p>Press the button to load the data...</p>
      )}
    </div>
    );
}


// var app_element = document.getElementById("app");
// var communityID  = app_element.getData();
ReactDOM.render(<CommunityCuration />, document.getElementById("app"));

export default CommunityCuration;
