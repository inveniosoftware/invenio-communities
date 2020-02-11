import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { Formik, Form, FieldArray, Field } from "formik";
import * as Yup from "yup";
import axios from "axios";
import _ from "lodash";
import { TextInput, SelectInput, RichInput, StringArrayInput, ObjectArrayInput } from "./forms";


const RequestPage = () => {
  const [globalError, setGlobalError] = useState(null);
  const [requestSuccess, setRequestSuccess] = useState(false);
  const [invitation, setInvitation] = useState(null);

  var request_id = window.location.pathname.split('/')[4];

  var declineInvitation = () => {
    var payload = {'response': 'decline'}
    axios
    .post(`/api/communities/members/requests/${request_id}`, payload)
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

var acceptInvitation = () => {
  var payload = {'response': 'accept'}
  axios
  .post(`/api/communities/members/requests/${request_id}`, payload)
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

  useEffect(() =>{
    fetch(`/api/communities/members/requests/${request_id}`)
      .then(res => res.json())
      .then(
        (result) => {
          setInvitation(result);
        },
        (error) => {
        }
      )
  console.log(invitation)
      }, [])
  if (!invitation){
    return ('Give us just a second.')
  }
  else{
    return (
      <div className="container">
        <h2>You have been invited to join the Community:<b> {invitation.community_name}</b> as a <b>{invitation.role}</b></h2>
        {requestSuccess ? (//maybe redirect to community page
          <div className="help-block">All is good</div>
        ) :
        <div>
        <button type="button" onClick={declineInvitation}>Decline</button>
        <button type="button" onClick={acceptInvitation}>Accept</button>
        </div>
        }
        {globalError ? (
          <div className="help-block">{globalError}</div>
        ) : null}
        </div>
    )}}


ReactDOM.render(<RequestPage />, document.getElementById("app"));

export default RequestPage;
