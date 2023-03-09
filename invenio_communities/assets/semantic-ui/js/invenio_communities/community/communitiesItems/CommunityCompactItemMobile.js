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
      <Image size="mini" src={result.links.logo} />

      <Item.Content verticalAlign="middle">
        <Item.Header as="h3" className="ui small header flex align-items-center mb-5">
          <a href={result.links.self_html} className="p-0">
            {result.metadata.title}
          </a>
        </Item.Header>

        <Item.Description
          dangerouslySetInnerHTML={{
            __html: _truncate(result.metadata.description, { length: 50 }),
          }}
        />
        <Item.Extra>
          <RestrictedLabel access={result.access.visibility} />
          <CommunityTypeLabel type={communityType} />
        </Item.Extra>
      </Item.Content>

      <div className="flex align-items-start">{actions}</div>
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
