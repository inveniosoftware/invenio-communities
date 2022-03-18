/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { useState, useRef } from "react";
import { Button, Form, Modal, Icon } from "semantic-ui-react";

import { CommunitiesApiClient } from "../../api";
import { i18next } from "@translations/invenio_communities/i18next";

// WARNING: This DOES NOT RENAME a community! It changes its id.
export const RenameCommunityButton = ({ community }) => {

  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState("");

  const formInputRef = React.useRef(null);

  const handleOpen = () => setModalOpen(true);

  const handleClose = () => setModalOpen(false);

  const handleRename = async (event) => {
    // stop event propagation so the submit event is restricted in the modal
    // form
    event.stopPropagation();
    const newId = formInputRef.current.value;
    const client = new CommunitiesApiClient();
    const response = await client.updateId(community.id, newId);
    if (response.code < 400) {
      window.location.href = `/communities/${newId}/settings`;
      handleClose();
    } else {
      const invalidIdError = response.errors
        .filter((error) => error.field === "id")
        .map((error) => error.messages[0]);
      setError(invalidIdError);
    }
  };

  return (
    <>
      <Button
        compact
        color="red"
        onClick={handleOpen}
        fluid
        icon
        labelPosition="left"
        type="button"
      >
        <Icon name="pencil"/>{i18next.t("Rename community")}
      </Button>

      <Modal open={modalOpen} onClose={handleClose} size="tiny">
        <Modal.Content>
          <Form onSubmit={handleRename}>
            <Form.Input
              label={i18next.t("Enter the new name of the community")}
              fluid
              input={{ ref: formInputRef }}
              {...(error
                ? {
                    error: {
                      content: error,
                      pointing: "above",
                    },
                  }
                : {})}
            />
          </Form>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={handleClose} floated="left">
            {i18next.t("Cancel")}
          </Button>
          <Button color="red" onClick={handleRename}>
            {i18next.t("Rename")}
          </Button>
        </Modal.Actions>
      </Modal>
    </>
  );
};
