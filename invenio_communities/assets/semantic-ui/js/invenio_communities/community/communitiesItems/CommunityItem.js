import React from "react";

import { CommunityItemComputer } from "./CommunityItemComputer";
import { CommunityItemMobile } from "./CommunityItemMobile";

export function CommunityItem({ result }) {
  return (
    <>
      <CommunityItemComputer result={result} />
      <CommunityItemMobile result={result} />
    </>
  );
}
