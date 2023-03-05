import React from "react";

import { CommunityCompactItemComputer } from "./CommunityCompactItemComputer";
import { CommunityCompactItemMobile } from "./CommunityCompactItemMobile";

export function CommunityCompactItem({ result }) {
  return (
    <>
      <CommunityCompactItemComputer result={result} />
      <CommunityCompactItemMobile result={result} />
    </>
  );
}
