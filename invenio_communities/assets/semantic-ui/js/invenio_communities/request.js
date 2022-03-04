/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { useState } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import _ from "lodash";
import { i18next } from "@translations/invenio_communities/i18next";

const RequestPage = () => {
  const [globalError, setGlobalError] = useState(null);
  const [requestDecline, setRequestDecline] = useState(false);

  const domContainer = document.getElementById("app");
  const formConfig = JSON.parse(domContainer.dataset.formConfig);

  var community = formConfig.community;
  var communityID = formConfig.community.id;
  var membership = formConfig.membership;
  var token = formConfig.token;

  var handleInvitation = (action) => {
    var payload = { token: token };
    axios
      .post(
        `/api/communities/${communityID}/members/requests/${membership.id}/${action}`,
        payload
      )
      .then((response) => {
        if (action === "accept") {
          window.location = `/communities/${communityID}/members/?tab=accepted`;
        } else {
          setRequestDecline(true);
        }
      })
      .catch((error) => {
        // TODO: handle nested fields
        if (error) {
          setGlobalError(error);
        }
        console.log(error.response.data);
      });
  };

  return (
    <div className="ui container">
      <h2>
        {i18next.t(
          "You have been invited to join the Community: {{title}} as a (n) {{role}}",
          {
            title: <b> "{community.title}"</b>,
            role: <b>{membership.role}</b>,
            interpolation: { escapeValue: false },
          }
        )}
      </h2>
      {requestDecline ? ( //maybe redirect to community page
        <div className="help-block">
          {i18next.t("You have succesfully declined the invitation.")}
        </div>
      ) : (
        <div>
          <div class="ui buttons">
            <button
              class="ui positive button"
              onClick={() => handleInvitation("accept")}
            >
              {i18next.t("Accept")}
            </button>
            <div class="or"></div>
            <button
              class="ui button"
              onClick={() => handleInvitation("reject")}
            >
              {i18next.t("Decline")}
            </button>
          </div>
        </div>
      )}
      {globalError ? <div className="help-block">{globalError}</div> : null}
    </div>
  );
};

ReactDOM.render(<RequestPage />, document.getElementById("app"));

export default RequestPage;
