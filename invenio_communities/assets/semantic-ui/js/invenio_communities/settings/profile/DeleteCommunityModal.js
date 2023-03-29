/*
 * This file is part of Invenio.
 * Copyright (C) 2023 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React, { Component } from "react";
import { Button, Icon, Modal, Message, Grid, Checkbox, Input } from "semantic-ui-react";
import PropTypes from "prop-types";
import { Trans } from "react-i18next";
import { communityErrorSerializer } from "../../api/serializers";
import { ErrorMessage, withCancel } from "react-invenio-forms";

export class DeleteCommunityModal extends Component {
  constructor(props) {
    super(props);
    this.INITIAL_STATE = {
      modalOpen: false,
      loading: false,
      checkboxMembers: false,
      checkboxRecords: false,
      checkboxSlug: false,
      inputSlug: "",
      error: undefined,
    };
    this.checkboxRef = React.createRef();
    this.openModalBtnRef = React.createRef();
    this.state = this.INITIAL_STATE;
  }

  componentDidUpdate(prevProps, prevState) {
    const { modalOpen } = this.state;
    if (modalOpen && modalOpen !== prevState.modalOpen) {
      const {
        current: { inputRef },
      } = this.checkboxRef;
      inputRef.current.focus();
    }
  }

  componentWillUnmount() {
    this.cancellableDelete && this.cancellableDelete.cancel();
  }

  handleInputChange = (event) => {
    this.setState({ inputSlug: event.target.value });
  };

  handleCheckboxChange = (e, { id, checked }) => {
    if (id === "members-confirm") {
      this.setState({
        checkboxMembers: checked,
      });
    }
    if (id === "records-confirm") {
      this.setState({
        checkboxRecords: checked,
      });
    }
    if (id === "slug-confirm") {
      this.setState({
        checkboxSlug: checked,
      });
    }
  };

  handleButtonDisabled = (slug) => {
    const { checkboxRecords, checkboxMembers, checkboxSlug, inputSlug } = this.state;
    return !(checkboxMembers && checkboxRecords && checkboxSlug && inputSlug === slug);
  };

  openConfirmModal = () => this.setState({ modalOpen: true });

  closeConfirmModal = () => {
    this.setState(this.INITIAL_STATE);
    this.openModalBtnRef?.current?.focus();
  };

  handleDelete = async () => {
    this.setState({ loading: true });
    const { onDelete, redirectURL } = this.props;

    this.cancellableDelete = withCancel(onDelete());
    try {
      await this.cancellableDelete.promise;

      if (redirectURL) {
        window.location.href = redirectURL;
      }

      this.closeConfirmModal();
    } catch (error) {
      if (error === "UNMOUNTED") return;
      console.error(error);
      const { message } = communityErrorSerializer(error);
      if (message) {
        this.setState({ error: message, loading: false });
      }
    }
  };

  render() {
    const {
      modalOpen,
      loading,
      error,
      checkboxMembers,
      checkboxRecords,
      checkboxSlug,
      inputSlug,
    } = this.state;
    const { label, community } = this.props;
    const communitySlug = community.slug;
    return (
      <>
        <Button
          ref={this.openModalBtnRef}
          compact
          negative
          onClick={this.openConfirmModal}
          fluid
          icon
          labelPosition="left"
          type="button"
          aria-haspopup="dialog"
          aria-controls="warning-modal"
          aria-expanded={modalOpen}
          id="delete-button"
        >
          <Icon name="trash" />
          {label}
        </Button>

        <Modal
          id="warning-modal"
          role="dialog"
          aria-labelledby="delete-button"
          open={modalOpen}
          onClose={this.closeConfirmModal}
          size="tiny"
        >
          <Modal.Header>{i18next.t("Permanently delete community")}</Modal.Header>
          <Modal.Content>
            <Trans>
              Are you <strong>absolutely sure</strong> you want to delete the community?
            </Trans>
          </Modal.Content>
          <Modal.Content>
            <Message negative>
              <Message.Header>
                <Grid columns={2} verticalAlign="middle">
                  <Grid.Column width={1}>
                    <Icon name="warning sign" />
                  </Grid.Column>
                  <Grid.Column width={15}>
                    {i18next.t("This action CANNOT be undone!")}
                  </Grid.Column>
                </Grid>
              </Message.Header>
              <Message.Content>
                <Checkbox
                  id="members-confirm"
                  ref={this.checkboxRef}
                  label={
                    /* eslint-disable-next-line jsx-a11y/label-has-associated-control */
                    <label>
                      <Trans>
                        <strong>All the members</strong> will be removed from the
                        community.
                      </Trans>
                    </label>
                  }
                  checked={checkboxMembers}
                  onChange={this.handleCheckboxChange}
                />
                <Checkbox
                  id="records-confirm"
                  label={
                    /* eslint-disable-next-line jsx-a11y/label-has-associated-control */
                    <label>
                      <Trans>
                        <strong>All the records</strong> will be removed from the
                        community.
                      </Trans>
                    </label>
                  }
                  checked={checkboxRecords}
                  onChange={this.handleCheckboxChange}
                />
                <Checkbox
                  id="slug-confirm"
                  label={
                    /* eslint-disable-next-line jsx-a11y/label-has-associated-control */
                    <label>
                      <Trans>
                        You <strong>CANNOT</strong> reuse the community identifier "
                        {{ communitySlug }}".
                      </Trans>
                    </label>
                  }
                  checked={checkboxSlug}
                  onChange={this.handleCheckboxChange}
                />
              </Message.Content>
            </Message>
          </Modal.Content>
          <Modal.Content>
            <Trans>
              Please type <strong>{{ communitySlug }}</strong> to confirm.
            </Trans>
            <Input fluid value={inputSlug} onChange={this.handleInputChange} />
          </Modal.Content>
          <Modal.Actions>
            {error && (
              <ErrorMessage
                header={i18next.t("Unable to delete")}
                content={i18next.t(error)}
                icon="exclamation"
                className="text-align-left"
                negative
              />
            )}
            <Button
              onClick={this.closeConfirmModal}
              disabled={loading}
              loading={loading}
              floated="left"
            >
              {i18next.t("Cancel")}
            </Button>
            <Button
              negative
              onClick={() => this.handleDelete()}
              loading={loading}
              disabled={this.handleButtonDisabled(communitySlug) || loading}
            >
              {i18next.t("Permanently delete")}
            </Button>
          </Modal.Actions>
        </Modal>
      </>
    );
  }
}

DeleteCommunityModal.propTypes = {
  onDelete: PropTypes.func.isRequired,
  redirectURL: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  community: PropTypes.object.isRequired,
};
