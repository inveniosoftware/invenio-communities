/*
 * This file is part of Invenio.
 * Copyright (C) 2021 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { useState, useRef } from "react";
import axios from "axios";
import { Button, Form, Modal, Icon } from "semantic-ui-react";

export const RenameCommunityButton = (props) => {
  const [modalOpen, setModalOpen] = useState(false);
  const formInputRef = React.useRef(null);

  const handleOpen = () => setModalOpen(true);

  const handleClose = () => setModalOpen(false);

  const handleRename = async () => {
    const newName = formInputRef.current.value;
    const resp = await axios.post(
      props.community.links.rename,
      { id: newName },
      {
        headers: { "Content-Type": "application/json" },
      }
    );
    handleClose();
    // TODO: replace it with proper link from the rename response
    window.location.href = `/communities/${newName}`;
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
        <Icon name="pencil"></Icon>Rename community
      </Button>

      <Modal open={modalOpen} onClose={handleClose} size="tiny">
        <Modal.Content>
          <Form>
            <Form.Input
              label="Enter the new name of the community"
              fluid
              input={{ ref: formInputRef }}
            />
          </Form>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={handleClose} floated="left">
            Cancel
          </Button>
          <Button color="red" onClick={handleRename}>
            Rename
          </Button>
        </Modal.Actions>
      </Modal>
    </>
  );
};
