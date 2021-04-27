/*
 * This file is part of Invenio.
 * Copyright (C) 2021 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { useState } from "react";
import PropTypes from "prop-types";
import axios from "axios";
import { Button, Icon, Modal } from "semantic-ui-react";

export const DeleteButton = (props) => {
  const [modalOpen, setModalOpen] = useState(false);

  const handleOpen = () => setModalOpen(true);

  const handleClose = () => setModalOpen(false);

  const handleDelete = async () => {
    try {
      const resp = await props.onDelete();
      handleClose();
      if (props.redirectURL) window.location.href = props.redirectURL;
    } catch (error) {
      props.onError(error);
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
        <Icon name="trash"></Icon>
        {props.label}
      </Button>

      <Modal open={modalOpen} onClose={handleClose} size="tiny">
        <Modal.Content>{props.confirmationMessage}</Modal.Content>
        <Modal.Actions>
          <Button onClick={handleClose} floated="left">
            Cancel
          </Button>
          <Button color="red" onClick={handleDelete}>
            Delete
          </Button>
        </Modal.Actions>
      </Modal>
    </>
  );
};
