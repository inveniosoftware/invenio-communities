import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import _ from "lodash";

const RequestPage = () => {
  const [globalError, setGlobalError] = useState(null);
  const [requestSuccess, setRequestSuccess] = useState(false);
  const [invitation, setInvitation] = useState(null);

  const domContainer = document.getElementById("app");
  const formConfig = JSON.parse(domContainer.dataset.formConfig);

  var community = formConfig.community
  var communityID = formConfig.community.id;
  var membership = formConfig.membership;
  var token = formConfig.token;

  var handleInvitation = (action) => {
    var payload = { 'token': token }
    axios
      .post(`/api/communities/${communityID}/members/requests/${membership.id}/${action}`, payload)
      .then(response => {
        setRequestSuccess(true)
      })
      .catch(error => {
        // TODO: handle nested fields
        if (error) {
          setGlobalError(error)
        }
        console.log(error.response.data);
      })
  }


  return (
    <div className="ui container">
      <h2>You have been invited to join the Community:<b> "{community.title}"</b> as a(n) <b>{membership.role}</b></h2>
      {requestSuccess ? (//maybe redirect to community page
        <div className="help-block">All is good</div>
      ) :
        <div>
          <div class="ui buttons">
            <button class="ui positive button" onClick={() =>handleInvitation('accept')}>Accept</button>
            <div class="or"></div>
            <button class="ui button" onClick={() =>handleInvitation('reject')}>Decline</button>
          </div>
        </div>
      }
      {globalError ? (
        <div className="help-block">{globalError}</div>
      ) : null}
    </div>
  )
}


ReactDOM.render(<RequestPage />, document.getElementById("app"));


export default RequestPage;
