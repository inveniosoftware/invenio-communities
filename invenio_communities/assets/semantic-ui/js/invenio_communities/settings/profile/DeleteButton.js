/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { useState } from "react";
import { Button, Icon, Modal } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";

export const DeleteButton = (props) => {
  const [modalOpen, setModalOpen] = useState(false);

  const handleOpen = () => setModalOpen(true);

  const handleClose = () => setModalOpen(false);

  const handleDelete = async () => {
    try {
      await props.onDelete();
      if (props.redirectURL) {
        window.location.href = props.redirectURL;
      }
    } catch (error) {
      props.onError(error);
    }
    handleClose();
  };

  return (
    <>
      <Button
        compact
        negative
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
            {i18next.t("Cancel")}
          </Button>
          <Button color="red" onClick={handleDelete}>
            {i18next.t("Delete")}
          </Button>
        </Modal.Actions>
      </Modal>
    </>
  );
};
