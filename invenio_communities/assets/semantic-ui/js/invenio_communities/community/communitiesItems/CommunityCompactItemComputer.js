// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// InvenioRDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CommunityTypeLabel } from "../components";
import _truncate from "lodash/truncate";
import React from "react";
import PropTypes from "prop-types";

import { Item, Image, Grid, Icon } from "semantic-ui-react";
import { RestrictedLabel } from "../access";

export const CommunityCompactItemComputer = ({ result, actions }) => {
  const communityType = result.ui?.type?.title_l10n;

  return (
    <Item
      key={result.id}
      className="computer tablet only justify-space-between community-item"
    >
      <Image as={Item.Image} size="tiny" src={result.links.logo} />
      <Grid>
        <Grid.Column width={10}>
          <Item.Content verticalAlign="middle">
            <Item.Header
              as="h3"
              className="ui small header flex align-items-center mb-5"
            >
              <a href={result.links.self_html} className="p-0">
                {result.metadata.title}
              </a>
            </Item.Header>

            <Item.Description>
              <div
                dangerouslySetInnerHTML={{
                  __html: _truncate(result.metadata.description, { length: 50 }),
                }}
              />
            </Item.Description>
            <Item.Extra>
              <RestrictedLabel access={result.access.visibility} />
              <CommunityTypeLabel type={communityType} />
            </Item.Extra>
          </Item.Content>
        </Grid.Column>
        <Grid.Column width={4}>
          <Item.Content>
            <Item.Meta>
              {result.ui.permissions.can_direct_publish && (
                <Icon name="paper plane outline" size="big" />
              )}
              {!result.ui.permissions.can_direct_publish && (
                <>
                  <Icon name="comments outline" size="big" />
                  <Icon corner="top right" name="question" size="small" fitted />
                </>
              )}
            </Item.Meta>
          </Item.Content>
        </Grid.Column>
      </Grid>
      <div className="flex align-items-start">{actions}</div>
    </Item>
  );
};
CommunityCompactItemComputer.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
};

CommunityCompactItemComputer.defaultProps = {
  actions: undefined,
};
