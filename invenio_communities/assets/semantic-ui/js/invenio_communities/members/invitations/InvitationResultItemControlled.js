/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import PropTypes from "prop-types";
import React, { Component } from "react";
import { withCancel } from "react-invenio-forms";
import { CommunityActionsApi } from "../../api";
import { errorSerializer } from "../../api/serializers";
import { randomBool } from "../mock";
import { InvitationResultItem } from "./InvitationResultItem";

export class InvitationResultItemControlled extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
      error: "",
      success: false,
    };

    this.actionsApi = new CommunityActionsApi(props.result.links);
  }

  componentWillUnmount() {
    this.cancellableDecline && this.cancellableDecline.cancel();
  }

  onRoleChange = (role) => {
    this.setState({ loading: true, success: false, error: "" });

    if (randomBool()) {
      setTimeout(
        () =>
          this.setState({
            loading: false,
            error: "",
            success: true,
            currentRole: role,
          }),
        500
      );
    } else {
      setTimeout(
        () =>
          this.setState({
            loading: false,
            error: "Example error message",
            success: false,
          }),
        500
      );
      throw Error;
    }
  };

  onCancel = async () => {
    this.setState({ loading: true });

    try {
      const payload = { content: "sorry!", format: "html" };

      this.cancellableDecline = withCancel(
        this.actionsApi.declineAction(payload)
      );
      await this.cancellableDecline.promise;

      this.setState({ loading: false, success: true, error: "" });
    } catch (error) {
      if (error === "UNMOUNTED") return;

      this.setState({
        loading: false,
        error: errorSerializer(error),
        success: false,
      });
    }
  };

  onView = () => {};

  onReInvite = () => {};

  render() {
    const { result, config } = this.props;
    const { loading, error, success, currentRole } = this.state;

    return (
      <InvitationResultItem
        roles={config.roles}
        currentRole={currentRole}
        invitation={result}
        onRoleChange={(role) => this.onRoleChange(role)}
        isLoading={loading}
        error={error}
        success={success}
        onErrorClose={() => this.setState({ error: "" })}
        onSuccessTimeOut={() => this.setState({ success: false })}
        onCancel={this.onCancel}
        onView={this.onView}
        onReInvite={this.onReInvite}
      />
    );
  }
}

InvitationResultItemControlled.propTypes = {
  result: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
};
