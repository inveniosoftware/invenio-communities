// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import { Image } from "react-invenio-forms";
import { Button, Icon, Item, Label, Grid, Header } from "semantic-ui-react";
import { DateTime } from "luxon";
import PropTypes from "prop-types";

export const CommunityCompactItemComputer = ({ result }) => {
  const communityType = result.ui?.type?.title_l10n;
  const visibility = result.access.visibility;
  const isPublic = visibility === "public";

  const label = {
    color: "red",
    icon: "lock",
    content: "restricted",
    corner: "left",
    size: "tiny",
  };
  // <Label size="tiny" className="negative" ribbon>
  //               <Icon name="ban" />
  //               restricted
  //             </Label>
  return (
    <Item key={result.id} className="computer tablet only flex community-item">
      <Image
        as={Item.Image}
        wrapped
        src={result.links.logo}
        className="community-logo"
      />
      <Grid>
        <Grid.Column width={12}>
          <Item.Content>
            <Item.Header size="medium" as={Header}>
              <a href={`/communities/${result.slug}`}>{result.metadata.title}</a>
            </Item.Header>
            <Item.Meta>
              <a
                href={result.metadata.website}
                target="_blank"
                rel="noopener noreferrer"
              >
                {result.metadata.website}
              </a>
            </Item.Meta>
            <Item.Description>
              <div
                className="truncate-lines-2"
                dangerouslySetInnerHTML={{
                  __html: result.metadata.description,
                }}
              />
            </Item.Description>

            <Item.Extra>
              <Label size="tiny" className="negative">
                <Icon name="lock" />
                restricted
              </Label>
              {communityType && (
                <Label size="tiny" className="primary">
                  <Icon name="tag" />
                  {communityType}
                </Label>
              )}
            </Item.Extra>
          </Item.Content>
        </Grid.Column>
        <Grid.Column width={4} textAlign="right">
          <Item.Content className="flex right-column">

          </Item.Content>
        </Grid.Column>
      </Grid>
    </Item>
  );
};

CommunityCompactItemComputer.propTypes = {
  result: PropTypes.object.isRequired,
};
