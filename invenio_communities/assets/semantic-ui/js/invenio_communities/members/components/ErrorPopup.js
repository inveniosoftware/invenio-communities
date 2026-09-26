/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { Icon, Label, Popup } from "semantic-ui-react";
import PropTypes from "prop-types";

export const ErrorPopup = ({
  trigger = <Icon name="exclamation circle" className="error" />,
  error = "",
}) => {
  return (
    <Popup
      basic
      className="p-0 borderless shadowless mb-1"
      open={!!error}
      position="top center"
      content={
        <Label
          content={error}
          basic
          className="mb-5 error"
          pointing="below"
          removeIcon="close"
        />
      }
      trigger={trigger}
    />
  );
};

ErrorPopup.propTypes = {
  trigger: PropTypes.node,
  error: PropTypes.string,
};
