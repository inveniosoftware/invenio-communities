// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CommunityTypeLabel } from "../labels";
import { RestrictedLabel } from "../labels";
import _truncate from "lodash/truncate";
import React from "react";
import { Image } from "react-invenio-forms";
import { Item } from "semantic-ui-react";
import PropTypes from "prop-types";

export const CommunityCompactItemMobile = ({ result, actions }) => {
  const communityType = result.ui?.type?.title_l10n;

  return (
    <Item key={result.id} className="mobile only justify-space-between">
      <Image size="mini" src={result.links.logo} alt="" />

      <Item.Content verticalAlign="middle">
        <Item.Header
          as="a"
          href={result.links.self_html}
          className="ui small header flex align-items-center mb-5"
        >
          {result.metadata.title}
        </Item.Header>

        {result.metadata.description && (
          <Item.Description
            as="p"
            dangerouslySetInnerHTML={{
              __html: _truncate(result.metadata.description, { length: 50 }),
            }}
          />
        )}

        <Item.Extra>
          <RestrictedLabel access={result.access.visibility} />
          <CommunityTypeLabel type={communityType} />
        </Item.Extra>
      </Item.Content>

      <div className="flex flex-direction-column align-items-center rel-mt-1">
        {actions}
      </div>
    </Item>
  );
};

CommunityCompactItemMobile.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
};

CommunityCompactItemMobile.defaultProps = {
  actions: undefined,
};
