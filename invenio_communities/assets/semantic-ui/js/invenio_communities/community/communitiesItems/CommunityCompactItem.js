import React from "react";
import PropTypes from "prop-types";

import { CommunityCompactItemComputer } from "./CommunityCompactItemComputer";
import { CommunityCompactItemMobile } from "./CommunityCompactItemMobile";

export function CommunityCompactItem({ result, actions }) {
  return (
    <>
      <CommunityCompactItemComputer result={result} actions={actions} />
      <CommunityCompactItemMobile result={result} actions={actions} />
    </>
  );
}

CommunityCompactItem.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
};

CommunityCompactItem.defaultProps = {
  actions: undefined,
};
