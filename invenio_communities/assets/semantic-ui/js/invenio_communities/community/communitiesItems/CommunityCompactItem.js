import React from "react";
import PropTypes from "prop-types";

import { CommunityCompactItemComputer } from "./CommunityCompactItemComputer";
import { CommunityCompactItemMobile } from "./CommunityCompactItemMobile";

export function CommunityCompactItem({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
  detailUrl,
  isCommunityDefault,
  recordRequests,
}) {
  return (
    <>
      <CommunityCompactItemComputer
        result={result}
        actions={actions}
        extraLabels={extraLabels}
        itemClassName={itemClassName}
        showPermissionLabel={showPermissionLabel}
        detailUrl={detailUrl}
        isCommunityDefault={isCommunityDefault}
        recordRequests={recordRequests}
      />
      <CommunityCompactItemMobile
        result={result}
        actions={actions}
        extraLabels={extraLabels}
        itemClassName={itemClassName}
        showPermissionLabel={showPermissionLabel}
        detailUrl={detailUrl}
        isCommunityDefault={isCommunityDefault}
        recordRequests={recordRequests}
      />
    </>
  );
}

CommunityCompactItem.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
  detailUrl: PropTypes.string,
  isCommunityDefault: PropTypes.bool.isRequired,
  recordRequests: PropTypes.object,
};

CommunityCompactItem.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
  detailUrl: undefined,
  recordRequests: {},
};
