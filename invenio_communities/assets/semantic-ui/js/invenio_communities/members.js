/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { Formik, Form, FieldArray, Field } from "formik";
import * as Yup from "yup";
import axios from "axios";
import _ from "lodash";

import { TextInput, SelectInput } from "./forms";


const COMMUNITY_ROLES = [
  { id: "A", display: "Administrator" },
  { id: "C", display: "Curator" },
  { id: "M", display: "Member" },
];

const COMMUNITY_ROLES_TO_ID = {
  'Administrator': 'A',
  'Curator': 'C',
  'Member': 'M'
}


const CommunityMembers = () => {
  const [globalError, setGlobalError] = useState(null);
  const [requestSuccess, setRequestSuccess] = useState(null);
  const [communityMembers, setCommunityMembers] = useState(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [communityRequests, setCommunityRequests] = useState(false);
  const [showIncomingRequests, setShowIncomingRequests] = useState(false);
  const [showOutgoingRequests, setShowOutgoingRequests] = useState(false);
  const [pageAccess, setPageAccess] = useState(false);


  var community_id = window.location.pathname.split('/')[2];

  var cancelRequest = (requestID) => {
    axios
    .delete(`/api/communities/members/requests/${requestID}`)
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


  var manageRequest = (requestID, role, response) => {
    console.log(communityRequests)
    var payload = {'role': role, 'response': response}
    axios
    .post(`/api/communities/members/requests/${requestID}`, payload)
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


  var modifyRequest = (requestID, role) => {
    console.log(communityRequests)
    var payload = {'role': role}
    axios
    .put(`/api/communities/members/requests/${requestID}`, payload)
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

  var removeMember = (userID) => {
    axios
    .delete(`/api/communities/${community_id}/members?user_id=${userID}`)
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

  var editMemberRole = (userID, role) => {
    var payload = {'user_id': userID, 'role': role}
    axios
    .put(`/api/communities/${community_id}/members`, payload)
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

  var joinCommunity = () => {
    var payload = {'request_type': 'request'}
    axios.
    post(`/api/communities/${community_id}/members`, payload)
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

  var displayInviteForm = () => {
    setShowInviteForm(!showInviteForm)
  }

  var displayIncomingRequests = () => {
    setShowIncomingRequests(!showIncomingRequests)
  }

  var displayOutgoingRequests = () => {
    setShowOutgoingRequests(!showOutgoingRequests)
  }

  useEffect(() => {
    fetch(`/api/communities/${community_id}/members`)
      .then(res => {
        if(res.status === 200){
          setPageAccess(true)
        }
        return res.json();
      })
      .then(
        (result) => {
            setCommunityMembers(result);
        },
        (error) => {
        }
      )
    fetch(`/api/communities/${community_id}/members/requests`)
      .then(res => {
        if(res.status === 200){
          setPageAccess(true);
        }
      return res.json();
    })
      .then(
        (result) => {
            setCommunityRequests(result);
        },
        (error) => {
        }
      )
  }, [])
  if (!communityMembers || !communityRequests) {
    return ('Give us just a second.');
  }
  else if(!pageAccess){
    return(
    <button type="button" onClick={joinCommunity}>Join this community</button>
    )
  }
  else {
    return (
      <div className="container">
        <h1>Community members</h1>
        <h3>Outgoing Community Requests ({communityRequests.out_count})</h3>
        {showOutgoingRequests ? (
          <div className="container">
          <button type="button" onClick={displayOutgoingRequests}>-</button>
          {communityRequests.out_requests.map( (request, index) => {
            request.role = COMMUNITY_ROLES_TO_ID[request.role]
            console.log(request.role)
            return (
            <div key={index}>
              <li>User email: {request.email}</li>
              <label>Invited as:</label>
              <select className="form-control" defaultValue={request.role}
               onChange={(event) => request.role=event.target.value}>
                {COMMUNITY_ROLES.map(choice =>(
                    <option key={choice.id} value={choice.id}>
                      {choice.display}
                    </option>
                ))}
                </select>
              <button type="button" onClick={() => modifyRequest(request.req_id, request.role)}>Modify role</button>
              <button type="button" onClick={() => cancelRequest(request.req_id)}>Cancel request</button>
            </div>
          )})}
          </div>
        ) : (
          <button type="button" onClick={displayOutgoingRequests}>+</button>
        ) }
        <h3>Incoming Community Requests ({communityRequests.inc_count})</h3>
        {showIncomingRequests ? (
          <div className="container">
          <button type="button" onClick={displayIncomingRequests}>-</button>
          {communityRequests.inc_requests.map( (request, index) => {
            let role = 'M';
            return (<div key={index}>
              <li>User email: {request.email}</li>
              <div className="form-group">
              <label>Role:</label>
              <select className="form-control" defaultValue='M'
               onChange={(event) => role=event.target.value}>
                {COMMUNITY_ROLES.map(choice =>(
                    <option key={choice.id} value={choice.id}>
                      {choice.display}
                    </option>
                ))}
                </select>
                </div>
                <button type="button" onClick={() => manageRequest(request.req_id, role, 'accept')}>Accept request</button>
                <button type="button" onClick={() => manageRequest(request.req_id, role, 'decline')}>Decline request</button>
            </div>
          )})}
          </div>
        ) : (
          <button type="button" onClick={displayIncomingRequests}>+</button>
        ) }
        <button type="button" onClick={displayInviteForm}>{!showInviteForm ? 'Invite a member': 'See the community members'}</button>
        {!showInviteForm ? (
          <table className="ui celled table">
            <thead>
              <tr>
                <th>#</th>
                <th>Email</th>
                <th>Role</th>
              </tr>
          </thead>
          <tbody>
          {communityMembers.map((member, index) => (
              <tr key={index}>
                <td>{index}</td>
                <td>{member.email}</td>
                <td>{member.role}</td>
                <td><button class="save icon" onClick={() => editMemberRole(member.user_id, member.role)}></button></td>
                <td><button class="remove circle icon" onClick={() => removeMember(member.user_id)}></button></td>
              </tr>
          ))}
          </tbody>
          </table>
            ) : (
            <div className="form-group">
            <h1>Invite a member</h1>
            <Formik
              initialValues={{
                email: "",
                role: "C",
                request_type: "invitation"
              }}
              validationSchema={Yup.object({
                email: Yup.string()
                  .required("Required"),
                role: Yup.string()
                  .required("Required")
                  .oneOf(
                    COMMUNITY_ROLES.map(c => {
                      return c.id;
                    })
                  ),
              })}
              onSubmit={(values, { setSubmitting, setErrors, setFieldError }) => {
                setSubmitting(true);
                const payload = _.pickBy(values, val => val !== "" && !_.isNil(val));
                var community_id = window.location.pathname.split('/')[2];
                axios
                  .post(`/api/communities/${community_id}/members`, payload)
                  .then(response => {
                    console.log(response);
                  })
                  .catch(error => {
                    // TODO: handle nested fields
                    if (error.response.data.errors) {
                      error.response.data.errors.map(({ field, message }) =>
                        setFieldError(field, message)
                      );
                    } else if (error.response.data.message) {
                      setGlobalError(error.response.data.message);
                    }
                    console.log(error.response.data);
                  })
                  .finally(() => setSubmitting(false));
              }} >
              {({ values, isSubmitting, isValid }) => (
                <Form>
                  <TextInput label="email" placeholder="example@email.com" name="email" />
                  <SelectInput choices={COMMUNITY_ROLES} label="Role" name="role" />
                  <button
                    disabled={!isValid || isSubmitting}
                    className="btn"
                    type="submit"
                  >
                    Submit
                    </button>
                  {globalError ? (
                    <div className="help-block">{globalError}</div>
                  ) : null}
                </Form>
              )}
            </Formik>
          </div>
      )}
      </div>
    );
  }
}


ReactDOM.render(<CommunityMembers />, document.getElementById("app"));

export default CommunityMembers;
