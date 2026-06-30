/*
 * SPDX-FileCopyrightText: 2023 CERN.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { Label, Icon } from "semantic-ui-react";

export const CommunityTypeLabel = ({ type = undefined, transparent = false }) => {
  if (type === undefined) return null;
  return (
    (transparent && (
      <div className="rel-mr-1">
        <Icon name="tag" />
        {type}
      </div>
    )) || (
      <Label size="small" horizontal className="primary">
        <Icon name="tag" />
        {type}
      </Label>
    )
  );
};

CommunityTypeLabel.propTypes = {
  type: PropTypes.string,
  transparent: PropTypes.bool,
};
