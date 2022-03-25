/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { useState, Component } from "react";
import { Button, Form, Modal, Icon } from "semantic-ui-react";

import { CommunityApi } from "../../api";
import { i18next } from "@translations/invenio_communities/i18next";
import { withCancel } from "react-invenio-forms";
import { communityErrorSerializer } from "../../api/serializers";

// WARNING: This DOES NOT RENAME a community! It changes its id.
export class RenameCommunityButton extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalOpen: false,
      error: "",
    };

    this.formInputRef = React.createRef();
  }

  componentWillUnmount() {
    this.cancellableRename && this.cancellableRename.cancel();
  }

  handleOpen = () => this.setState({ modalOpen: true });

  handleClose = () => this.setState({ modalOpen: false });

  handleRename = async (event) => {
    // stop event propagation so the submit event is restricted in the modal
    // form
    event.stopPropagation();
    const { community } = this.props;
    const newId = this.formInputRef.current.value;
    const client = new CommunityApi();

    this.cancellableRename = withCancel(client.updateId(community.id, newId));

    try {
      await this.cancellableRename.promise;

      window.location.href = `/communities/${newId}/settings`;
      this.handleClose();
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { errors } = communityErrorSerializer(error);

      if (errors) {
        const invalidIdError = errors
          .filter((error) => error.field === "id")
          .map((error) => error.messages[0]);
        this.setState({ error: invalidIdError });
      }
    }
  };

  render() {
    const { modalOpen, error } = this.state;

    return (
      <>
        <Button
          compact
          negative
          onClick={this.handleOpen}
          fluid
          icon
          labelPosition="left"
          type="button"
        >
          <Icon name="pencil" />
          {i18next.t("Rename community")}
        </Button>

        <Modal open={modalOpen} onClose={this.handleClose} size="tiny">
          <Modal.Content>
            <Form onSubmit={this.handleRename}>
              <Form.Input
                label={i18next.t("Enter the new name of the community")}
                fluid
                input={{ ref: this.formInputRef }}
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
            <Button onClick={this.handleClose} floated="left">
              {i18next.t("Cancel")}
            </Button>
            <Button color="red" onClick={this.handleRename}>
              {i18next.t("Rename")}
            </Button>
          </Modal.Actions>
        </Modal>
      </>
    );
  }
}
