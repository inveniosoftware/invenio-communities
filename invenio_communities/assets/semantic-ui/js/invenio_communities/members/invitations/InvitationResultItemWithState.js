/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { InvitationResultItem } from "./InvitationResultItem";
import PropTypes from "prop-types";
import { randomBool } from "../mock";

export class InvitationResultItemWithState extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
      error: "",
      success: false,
      currentRole: props.result.role.title,
    };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    const { success } = this.state;
    const timerAlreadySet = !!this.successTimer;

    if (success) {
      if (timerAlreadySet) {
        clearTimeout(this.successTimer);
      }

      this.successTimer = setTimeout(
        () => this.setState({ success: false }),
        3000
      );
    }
  }

  componentWillUnmount() {
    this.successTimer && clearTimeout(this.successTimer);
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
    }
  };

  render() {
    const { result, index } = this.props;
    const { loading, error, success, currentRole } = this.state;

    return (
      <InvitationResultItem
        currentRole={currentRole}
        invitation={result}
        key={index}
        onRoleChange={(role) => this.onRoleChange(role)}
        isLoading={loading}
        error={error}
        success={success}
        onErrorClose={() => this.setState({ error: "" })}
      />
    );
  }
}

InvitationResultItemWithState.propTypes = {
  result: PropTypes.object.isRequired,
  index: PropTypes.number.isRequired,
};
