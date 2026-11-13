/*
 * SPDX-FileCopyrightText: 2023-2024 CERN.
 * SPDX-License-Identifier: MIT
 */

import { RestoreConfirmation } from "./RestoreConfirmation";
import TombstoneForm from "./TombstoneForm";
import { Component } from "react";
import PropTypes from "prop-types";
import { Button, Modal, Icon } from "semantic-ui-react";
import { ActionModal, ActionForm } from "@js/invenio_administration";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/invenio_communities/i18next";

export class RecordResourceActions extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    };
  }

  onModalTriggerClick = (
    e,
    { payloadSchema, dataName, dataActionKey, actionConfig }
  ) => {
    const { resource } = this.props;

    if (dataActionKey === "delete") {
      this.setState({
        modalOpen: true,
        modalHeader: i18next.t("Delete community"),
        modalBody: (
          <TombstoneForm
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            resource={resource}
          />
        ),
      });
    } else if (dataActionKey === "restore") {
      this.setState({
        modalOpen: true,
        modalHeader: i18next.t("Restore community"),
        modalBody: (
          <RestoreConfirmation
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            resource={resource}
          />
        ),
      });
    } else {
      this.setState({
        modalOpen: true,
        modalHeader: dataName,
        modalBody: (
          <ActionForm
            actionKey={dataActionKey}
            actionSchema={payloadSchema}
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            resource={resource}
            actionConfig={actionConfig}
          />
        ),
      });
    }
  };

  closeModal = () => {
    this.setState({
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    });
  };

  handleSuccess = () => {
    const { successCallback } = this.props;
    this.setState({
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    });
    successCallback();
  };

  render() {
    const { actions, Element = Button, resource } = this.props;
    const { modalOpen, modalHeader, modalBody } = this.state;
    const isDeleted = resource?.deletion_status?.is_deleted;
    return (
      <>
        {Object.entries(actions || {}).map(([actionKey, actionConfig]) => {
          const modalData = {
            payloadSchema: actionConfig.payload_schema,
            dataName: actionConfig.text,
            dataActionKey: actionKey,
            actionConfig: actionConfig,
          };
          const handleClick = (e) => this.onModalTriggerClick(e, modalData);
          if (actionKey === "delete" && !isDeleted) {
            return (
              <Element
                key={actionKey}
                onClick={handleClick}
                icon
                fluid
                labelPosition="left"
              >
                <Icon name="trash alternate" />
                {actionConfig.text}...
              </Element>
            );
          } else if (actionKey === "restore" && isDeleted) {
            return (
              <Element
                key={actionKey}
                onClick={handleClick}
                icon
                fluid
                labelPosition="left"
              >
                <Icon name="undo" />
                {actionConfig.text}...
              </Element>
            );
          } else if (!isDeleted && actionKey !== "restore") {
            return (
              <Element key={actionKey} onClick={handleClick}>
                {actionConfig.text}...
              </Element>
            );
          }
          return null;
        })}
        <ActionModal modalOpen={modalOpen} resource={resource}>
          {modalHeader && <Modal.Header>{modalHeader}</Modal.Header>}
          {!_isEmpty(modalBody) && modalBody}
        </ActionModal>
      </>
    );
  }
}

RecordResourceActions.propTypes = {
  resource: PropTypes.object,
  successCallback: PropTypes.func.isRequired,
  actions: PropTypes.objectOf(
    PropTypes.shape({
      text: PropTypes.string,
      payload_schema: PropTypes.object,
      order: PropTypes.number,
    })
  ),
  Element: PropTypes.elementType,
};
