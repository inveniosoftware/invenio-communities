/*
 * This file is part of Invenio.
 * Copyright (C) 2025 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Checkbox } from "semantic-ui-react";
import { errorSerializer } from "../../api/serializers";
import { ErrorPopup } from "./ErrorPopup";
import { SuccessIcon } from "./SuccessIcon";

export class GroupNotificationToggle extends Component {
  constructor(props) {
    super(props);
    this.state = {
      notificationEnabled: props.initialValue ?? true,
      actionSuccess: false,
      error: undefined,
    };
  }

  handleToggle = async (e, { checked }) => {
    const { member, updateAction } = this.props;

    this.setState({ actionSuccess: false, error: undefined });

    try {
      await updateAction(member, checked);
      this.setState({
        notificationEnabled: checked,
        actionSuccess: true,
        error: undefined,
      });
    } catch (error) {
      this.setState({
        actionSuccess: false,
        error: errorSerializer(error),
      });
    }
  };

  render() {
    const { notificationEnabled, actionSuccess, error } = this.state;

    return (
      <div className="display-inline-flex flex-direction-row-reverse">
        <Checkbox toggle checked={notificationEnabled} onChange={this.handleToggle} />
        <div className="ml-15 action-status-container">
          {actionSuccess && <SuccessIcon timeOutDelay={3000} show={actionSuccess} />}
          {error && <ErrorPopup error={error} />}
        </div>
      </div>
    );
  }
}

GroupNotificationToggle.propTypes = {
  member: PropTypes.object.isRequired,
  initialValue: PropTypes.bool,
  updateAction: PropTypes.func.isRequired,
};

GroupNotificationToggle.defaultProps = {
  initialValue: true,
};
