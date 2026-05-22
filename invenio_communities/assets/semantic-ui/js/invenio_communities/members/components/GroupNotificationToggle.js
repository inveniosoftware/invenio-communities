/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
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
      notificationEnabled: props.initialValue ?? false,
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
    const { readOnly } = this.props;
    const { notificationEnabled, actionSuccess, error } = this.state;

    if (readOnly) {
      return notificationEnabled ? i18next.t("Enabled") : i18next.t("Disabled");
    }

    return (
      <div className="display-inline-flex flex-direction-row-reverse align-items-center">
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
  updateAction: PropTypes.func,
  readOnly: PropTypes.bool,
};

GroupNotificationToggle.defaultProps = {
  initialValue: false,
  readOnly: false,
  updateAction: undefined,
};
