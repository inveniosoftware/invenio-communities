// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import { CommunityTypeLabel } from "../labels";
import { RestrictedLabel } from "../labels";
import React from "react";
import { Image } from "react-invenio-forms";
import { Button, Item, Grid, Header } from "semantic-ui-react";
import { DateTime } from "luxon";
import PropTypes from "prop-types";

export const CommunityItemComputer = ({ result }) => {
  const communityType = result.ui?.type?.title_l10n;

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
              <a href={result.links.self_html}>{result.metadata.title}</a>
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
              <RestrictedLabel access={result.access.visibility} />
              <CommunityTypeLabel type={communityType} />
            </Item.Extra>
          </Item.Content>
        </Grid.Column>
        <Grid.Column width={4} textAlign="right">
          <Item.Content className="flex right-column">
            {result.ui.permissions.can_update && (
              <Item.Description>
                <Button
                  compact
                  size="small"
                  href={result.links.settings_html}
                  className="mt-0"
                  labelPosition="left"
                  icon="edit"
                  content={i18next.t("Edit")}
                />
              </Item.Description>
            )}
            <Item.Extra className="text-align-right">
              {i18next.t("Created: ")}
              {DateTime.fromISO(result.created).toLocaleString(i18next.language)}
            </Item.Extra>
          </Item.Content>
        </Grid.Column>
      </Grid>
    </Item>
  );
};

CommunityItemComputer.propTypes = {
  result: PropTypes.object.isRequired,
};
