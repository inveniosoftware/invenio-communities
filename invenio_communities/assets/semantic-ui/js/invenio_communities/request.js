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
import { i18next } from "@translations/invenio_communities/i18next";
import { Button, Container, Header } from "semantic-ui-react";

const RequestPage = () => {
  const [globalError, setGlobalError] = useState(null);
  const [requestDecline, setRequestDecline] = useState(false);

  const domContainer = document.getElementById("app");
  const formConfig = JSON.parse(domContainer.dataset.formConfig);

  const {
    community,
    community: { id },
    membership,
    token,
  } = formConfig;

  const handleInvitation = async (action) => {
    const payload = { token: token };
    try {
      await axios.post(
        `/api/communities/${communityID}/members/requests/${membership.id}/${action}`,
        payload
      );
      if (action === "accept") {
        window.location = `/communities/${communityID}/members/?tab=accepted`;
      } else {
        setRequestDecline(true);
      }
    } catch (error) {
      // TODO: handle nested fields
      if (error) {
        setGlobalError(error);
      }
      console.log(error.response.data);
    }
  };

  return (
    <Container>
      <Header as="h2">
        {i18next.t(
          "You have been invited to join the Community: {{title}} as a (n) {{role}}",
          {
            title: <b> "{community.title}"</b>,
            role: <b>{membership.role}</b>,
            interpolation: { escapeValue: false },
          }
        )}
      </Header>
      {requestDecline ? ( //maybe redirect to community page
        <>{i18next.t("You have successfully declined the invitation.")}</>
      ) : (
        <Button.Group>
          <Button positive={} onClick={() => handleInvitation("accept")}>
            {i18next.t("Accept")}
          </Button>
          <Button.Or />
          <Button onClick={() => handleInvitation("reject")}>
            {i18next.t("Decline")}
          </Button>
        </Button.Group>
      )}
      {globalError ? <>{globalError}</> : null}
    </Container>
  );
};

ReactDOM.render(<RequestPage />, document.getElementById("app"));

export default RequestPage;
