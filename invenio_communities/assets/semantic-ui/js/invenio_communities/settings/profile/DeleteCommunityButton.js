import React, { useState } from "react";
import PropTypes from "prop-types";
import axios from "axios";
import { Button, Icon, Modal } from "semantic-ui-react";

export const DeleteCommunityButton = (props) => {
  const [modalOpen, setModalOpen] = useState(false);

  const handleOpen = () => setModalOpen(true);

  const handleClose = () => setModalOpen(false);

  const handleDelete = async () => {
    const resp = await axios.delete(
      `/api/communities/${props.community.id}`,
      {},
      {
        headers: { "Content-Type": "application/json" },
      }
    );
    handleClose();
    window.location.href = `/communities`;
  };

  return (
    <>
      <Button
        compact
        color="red"
        onClick={handleOpen}
        fluid
        icon
        type="button"
        labelPosition="left"
      >
        <Icon name="trash alternate outline" />
        Delete community
      </Button>

      <Modal open={modalOpen} onClose={handleClose} size="tiny">
        <Modal.Content>
          <h3>Are you sure you want to delete this community?</h3>
        </Modal.Content>
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
