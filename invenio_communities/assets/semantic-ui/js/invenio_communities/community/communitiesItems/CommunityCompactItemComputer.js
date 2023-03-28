// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// InvenioRDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _truncate from "lodash/truncate";
import PropTypes from "prop-types";
import React from "react";
import { CommunityTypeLabel } from "../labels";

import { Grid, Container, Image, Item } from "semantic-ui-react";
import { RestrictedLabel } from "../labels";

export const CommunityCompactItemComputer = ({
  result,
  actions,
  extraLabels,
  itemClassName,
}) => {
  const { metadata, links, access, id } = result;
  const ui = result.ui;

  const communityType = ui?.type?.title_l10n;

  return (
    <Item
      key={id}
      className={`computer tablet only justify-space-between community-item ${itemClassName}`}
    >
      <Image as={Item.Image} size="tiny" src={links.logo} />
      <Grid>
        <Grid.Column width={10}>
          <Item.Content verticalAlign="middle">
            <Item.Header
              as="h3"
              className="ui small header flex align-items-center mb-5"
            >
              <a href={links.self_html} className="p-0">
                {metadata.title}
              </a>
            </Item.Header>

            <Item.Description>
              <div
                dangerouslySetInnerHTML={{
                  __html: _truncate(metadata.description, { length: 50 }),
                }}
              />
            </Item.Description>
            <Item.Extra>
              <RestrictedLabel access={access.visibility} />
              <CommunityTypeLabel type={communityType} />
              {extraLabels}
            </Item.Extra>
          </Item.Content>
        </Grid.Column>
      </Grid>
      <Container fluid>
        <div className="flex flex-direction-column align-items-end">{actions}</div>
      </Container>
    </Item>
  );
};
CommunityCompactItemComputer.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
};

CommunityCompactItemComputer.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
};
