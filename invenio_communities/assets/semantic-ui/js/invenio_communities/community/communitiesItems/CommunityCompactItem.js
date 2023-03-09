import React from "react";
import PropTypes from "prop-types";

import { CommunityCompactItemComputer } from "./CommunityCompactItemComputer";
import { CommunityCompactItemMobile } from "./CommunityCompactItemMobile";

export function CommunityCompactItem({ result, actions, extraLabels, itemClassName }) {
  return (
    <>
      <CommunityCompactItemComputer
        result={result}
        actions={actions}
        extraLabels={extraLabels}
        itemClassName={itemClassName}
      />
      <CommunityCompactItemMobile
        result={result}
        actions={actions}
        extraLabels={extraLabels}
        itemClassName={itemClassName}
      />
    </>
  );
}

CommunityCompactItem.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
};

CommunityCompactItem.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
};
