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
import { Grid } from "semantic-ui-react";
import { TextField, SelectField } from "react-invenio-forms";

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
var communityID = formConfig.community.id;

var userRole = formConfig.communityMember.role;
var urlObject = new URL(window.location);

const COMMUNITY_ROLES = [
  { value: "admin", text: "Administrator" },
  { value: "curator", text: "Curator" },
  { value: "member", text: "Member" },
];

const CommunityMembers = () => {
  const [requestSuccess, setRequestSuccess] = useState(false);
  const [globalError, setGlobalError] = useState(null);
  const [communityMembers, setCommunityMembers] = useState(null);
  const [activeTab, setActiveTab] = useState(null);
  const [pageAccess, setPageAccess] = useState(false);

  var removeMembership = (membershipID) => {
    axios
      .delete(
        `/api/communities/${communityID}/members/requests/${membershipID}`
      )
      .then((response) => {
        setRequestSuccess(true);
      })
      .catch((error) => {
        // TODO: handle nested fields
        if (error) {
          setGlobalError(error);
        }
        console.log(error.response.data);
      });
  };

  var manageRequest = (membershipID, role, action, message = null) => {
    var payload = { role: role };
    if (message) {
      payload["message"] = message;
    }
    axios
      .post(
        `/api/communities/${communityID}/members/requests/${membershipID}/${action}`,
        payload
      )
      .then((response) => {
        setRequestSuccess(true);
      })
      .catch((error) => {
        // TODO: handle nested fields
        if (error) {
          setGlobalError(error);
        }
        console.log(error.response.data);
      });
  };

  var modifyMembership = (membershipID, role) => {
    var payload = { role: role };
    axios
      .put(
        `/api/communities/${communityID}/members/requests/${membershipID}`,
        payload
      )
      .then((response) => {
        setRequestSuccess(true);
      })
      .catch((error) => {
        // TODO: handle nested fields
        if (error) {
          setGlobalError(error);
        }
        console.log(error.response.data);
      });
  };

  var joinCommunity = () => {
    var payload = { request_type: "request" };
    axios
      .post(`/api/communities/${communityID}/members`, payload)
      .then((response) => {
        setRequestSuccess(true);
      })
      .catch((error) => {
        // TODO: handle nested fields
        if (error) {
          setGlobalError(error);
        }
        console.log(error.response.data);
      });
  };

  var changeTab = (value) => {
    urlObject.searchParams.set("tab", value);
    window.location = urlObject.toString();
  };

  var fetchAndSetMemberships = (status) => {
    var includeRequests;
    if (status !== "accepted") {
      includeRequests = true;
    } else {
      includeRequests = false;
    }
    fetch(
      `/api/communities/${communityID}/members/${status}?include_requests=${includeRequests}`
    )
      .then((res) => {
        if (res.status === 200) {
          setPageAccess(true);
        } else if (res.status === 403) {
          setCommunityMembers(true);
        }
        return res.json();
      })
      .then(
        (result) => {
          setCommunityMembers(result);
        },
        (error) => {}
      );
  };

  useEffect(() => {
    let currentTab = urlObject.searchParams.get("tab");
    setActiveTab(currentTab);
    if (!currentTab) {
      urlObject.searchParams.set("tab", "accepted");
      window.location = urlObject.toString();
    }
    if (currentTab !== "addition") {
      fetchAndSetMemberships(currentTab);
    } else {
      setPageAccess(true);
    }
  }, []);
  if (!communityMembers && (activeTab !== "addition" || activeTab === null)) {
    return (
      <div class="container ui">
        <div class="ui active centered inline loader"></div>
      </div>
    );
  } else if (!pageAccess) {
    return (
      <div class="container ui">
        {requestSuccess ? (
          <p>You have succesfully requested to join the community</p>
        ) : (
          <button class="ui positive button" onClick={joinCommunity}>
            Join this community
          </button>
        )}
      </div>
    );
  } else {
    return (
      <div class="container ui">
        {userRole === "admin" ? (
          <div class="ui top secondary pointing menu">
            <a
              class={activeTab === "accepted" ? "active item" : "item"}
              onClick={() => changeTab("accepted")}
            >
              Members
            </a>
            <a
              class={activeTab === "pending" ? "active item" : "item"}
              onClick={() => changeTab("pending")}
            >
              Pending Memberships
            </a>
            <a
              class={activeTab === "rejected" ? "active item" : "item"}
              onClick={() => changeTab("rejected")}
            >
              Rejected Memberships
            </a>
            <a
              class={activeTab === "addition" ? "active item" : "item"}
              onClick={() => changeTab("addition")}
            >
              Invite Member
            </a>
          </div>
        ) : null}
        {(() => {
          switch (activeTab) {
            case "accepted":
              return (
                <div>
                  <h1>Community members</h1>
                  <table class="ui celled table">
                    <thead>
                      <tr>
                        <th>Username</th>
                        <th>Role</th>
                        {userRole === "admin" ? <th>Remove Member</th> : null}
                      </tr>
                    </thead>
                    <tbody>
                      {communityMembers.hits.hits.map((member, index) => (
                        <tr key={index}>
                          <td>{member.username || member.user_id}</td>
                          {userRole === "admin" ? (
                            <td>
                              <select
                                defaultValue={member.role}
                                onChange={(event) =>
                                  (member.role = event.target.value)
                                }
                              >
                                {COMMUNITY_ROLES.map((choice) => (
                                  <option
                                    key={choice.value}
                                    value={choice.value}
                                  >
                                    {choice.text}
                                  </option>
                                ))}
                              </select>
                              <button
                                onClick={() =>
                                  modifyMembership(member.id, member.role)
                                }
                              >
                                <i class="ui check icon"></i>
                              </button>
                            </td>
                          ) : (
                            <td>{member.role}</td>
                          )}
                          {userRole === "admin" ? (
                            <td>
                              <button
                                onClick={() => removeMembership(member.id)}
                              >
                                <i class="ui ban icon"></i>
                              </button>
                            </td>
                          ) : null}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              );
            case "pending":
              return (
                <div>
                  <h1>Community member requests</h1>
                  <table class="ui celled table">
                    <thead>
                      <tr>
                        <th>Username or Email</th>
                        <th>Role</th>
                        <th>Request Type</th>
                        <th>Comments</th>
                        <th>Accept</th>
                        <th>Reject</th>
                      </tr>
                    </thead>
                    <tbody>
                      {communityMembers.hits.hits.map((member, index) => (
                        <tr key={index}>
                          <td>
                            {member.username || member.email || member.user_id}
                          </td>
                          <td>
                            <select
                              defaultValue={member.role}
                              onChange={(event) =>
                                (member.role = event.target.value)
                              }
                            >
                              {COMMUNITY_ROLES.map((choice) => (
                                <option key={choice.value} value={choice.value}>
                                  {choice.text}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td>{member.request.request_type}</td>
                          <td>
                            {member.request.comments.map((comment, index) => (
                              <p key={index}>{comment.message}</p>
                            ))}
                          </td>
                          <td>
                            <button
                              disabled={
                                member.request.request_type === "invitation"
                              }
                              onClick={() =>
                                manageRequest(member.id, member.role, "accept")
                              }
                            >
                              <i class="ui check icon"></i>
                            </button>
                          </td>
                          <td>
                            <button
                              disabled={
                                member.request.request_type === "invitation"
                              }
                              onClick={() =>
                                manageRequest(member.id, member.role, "reject")
                              }
                            >
                              <i class="ui ban icon"></i>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              );
            case "rejected":
              return (
                <div>
                  <h1>Community members</h1>
                  <table class="ui celled table">
                    <thead>
                      <tr>
                        <th>Username or Email</th>
                        <th>Comments</th>
                        {userRole === "admin" ? <th>Remove request</th> : null}
                      </tr>
                    </thead>
                    <tbody>
                      {communityMembers.hits.hits.map((member, index) => (
                        <tr key={index}>
                          <td>
                            {member.username || member.email || member.user_id}
                          </td>
                          <td>
                            {member.request.comments.map((comment, index) => (
                              <p>{comment.message}</p>
                            ))}
                          </td>
                          {userRole === "admin" ? (
                            <td>
                              <button
                                onClick={() => removeMembership(member.id)}
                              >
                                <i class="ui ban icon"></i>
                              </button>
                            </td>
                          ) : null}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              );
            case "addition":
              return (
                <div class="form-group">
                  <h1>Invite a member</h1>
                  <Formik
                    initialValues={{
                      email: "",
                      role: "C",
                      comment: "",
                    }}
                    validationSchema={Yup.object({
                      email: Yup.string().required("Required"),
                      role: Yup.string()
                        .required("Required")
                        .oneOf(
                          COMMUNITY_ROLES.map((c) => {
                            return c.value;
                          })
                        ),
                    })}
                    onSubmit={(
                      values,
                      { setSubmitting, setErrors, setFieldError }
                    ) => {
                      setSubmitting(true);
                      const payload = _.pickBy(
                        values,
                        (val) => val !== "" && !_.isNil(val)
                      );
                      var communityID = window.location.pathname.split("/")[2];
                      axios
                        .post(
                          `/api/communities/${communityID}/members`,
                          payload
                        )
                        .then((response) => {
                          console.log(response);
                        })
                        .catch((error) => {
                          // TODO: handle nested fields
                          if (error.response.data.errors) {
                            error.response.data.errors.map(
                              ({ field, messages }) =>
                                setFieldError(field, messages[0])
                            );
                          } else if (error.response.data.message) {
                            setGlobalError(error.response.data.message);
                          }
                          console.log(error.response.data);
                        })
                        .finally(() => {
                          setSubmitting(false);
                          changeTab("pending");
                        });
                    }}
                  >
                    {({ values, isSubmitting, isValid }) => (
                      <Form>
                        <Grid>
                          <Grid.Column width={4}>
                            <TextField
                              label="Email"
                              placeholder="example@email.com"
                              fieldPath="email"
                              fluid
                            />
                          </Grid.Column>
                          <Grid.Column width={3}>
                            <SelectField
                              defaultValue={COMMUNITY_ROLES[2].value}
                              options={COMMUNITY_ROLES}
                              label="Role"
                              fieldPath="role"
                              fluid
                            />
                          </Grid.Column>
                          <Grid.Column width={4}>
                            <TextField
                              label="Comment"
                              placeholder="Write a message to the invited person"
                              fieldPath="comment"
                              fluid
                            />
                          </Grid.Column>
                        </Grid>
                        <br></br>
                        <button
                          disabled={!isValid || isSubmitting}
                          class="ui positive button small"
                          type="submit"
                        >
                          Submit
                        </button>
                        {globalError ? (
                          <div class="help-block">{globalError}</div>
                        ) : null}
                      </Form>
                    )}
                  </Formik>
                </div>
              );
          }
        })()}
      </div>
    );
  }
};

ReactDOM.render(<CommunityMembers />, document.getElementById("app"));

export default CommunityMembers;
