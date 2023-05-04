import React from "react";
import PropTypes from "prop-types";
import { Label, Icon } from "semantic-ui-react";

export const CommunityTypeLabel = ({ type }) => {
  if (type === undefined) return null;
  return (
    <Label size="small" horizontal className="primary">
      <Icon name="tag" />
      {type}
    </Label>
  );
};

CommunityTypeLabel.propTypes = {
  type: PropTypes.string,
};

CommunityTypeLabel.defaultProps = {
  type: undefined,
};
