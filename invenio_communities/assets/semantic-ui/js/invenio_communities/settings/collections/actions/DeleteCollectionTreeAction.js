// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import { Button, Modal, Message, Checkbox } from "semantic-ui-react";
import { communityErrorSerializer } from "../../../api/serializers";

class DeleteCollectionTreeAction extends Component {
  state = {
    error: "",
    cascade: false,
  };

  setGlobalError = (error) => {
    const { message } = communityErrorSerializer(error);
    this.setState({ error: message });
  };

  handleCascadeChange = (e, { checked }) => {
    this.setState({ cascade: checked });
  };

  handleDelete = async () => {
    const { collectionTree, collectionApi } = this.props;
    const { cascade } = this.state;

    try {
      await collectionApi.delete_collection_tree(
        collectionTree.slug,
        {},
        null,
        cascade
      );
      this.props.onSuccess();
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { message, errors } = communityErrorSerializer(error);

      if (message) {
        this.setGlobalError(error);
      }
    }
  };

  render() {
    const { error, cascade } = this.state;
    const { hasCollections } = this.props;

    return (
      <>
        <Modal.Content>
          {error && (
            <Message negative>
              <Message.Header>{i18next.t("Error")}</Message.Header>
              <p>{error}</p>
            </Message>
          )}
          <p>{this.props.confirmationMessage}</p>
          {hasCollections && (
            <div className="rel-mt-2">
              <Message info>
                <Message.Header>
                  {i18next.t("This category contains collections")}
                </Message.Header>
                <p>
                  {i18next.t(
                    "You must check the option below to delete the category along with all its collections."
                  )}
                </p>
              </Message>
              <Checkbox
                label={i18next.t("Delete this category and all its collections")}
                checked={cascade}
                onChange={this.handleCascadeChange}
              />
              {cascade && (
                <Message warning className="rel-mt-1">
                  <Message.Header>{i18next.t("Warning")}</Message.Header>
                  <p>
                    {i18next.t(
                      "This will permanently delete this category and ALL of its collections. This action cannot be undone."
                    )}
                  </p>
                </Message>
              )}
            </div>
          )}
        </Modal.Content>
        <Modal.Actions>
          <div className="flex justify-space-between">
            <Button onClick={this.props.handleCancel}>{i18next.t("Cancel")}</Button>
            <Button
              negative
              onClick={this.handleDelete}
              disabled={hasCollections && !cascade}
            >
              {i18next.t("Delete")}
            </Button>
          </div>
        </Modal.Actions>
      </>
    );
  }
}

DeleteCollectionTreeAction.propTypes = {
  collectionTree: PropTypes.object.isRequired,
  hasCollections: PropTypes.bool,
  onSuccess: PropTypes.func,
  handleCancel: PropTypes.func,
  confirmationMessage: PropTypes.string.isRequired,
  collectionApi: PropTypes.object.isRequired,
};

DeleteCollectionTreeAction.defaultProps = {
  hasCollections: false,
  onSuccess: () => {},
  handleCancel: () => {},
};

export default DeleteCollectionTreeAction;
