// This file is part of InvenioRDM
// Copyright (C) 2022-2024 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_communities/i18next";
import { CommunityTypeLabel } from "../labels";
import { RestrictedLabel } from "../labels";
import React from "react";
import { Image } from "react-invenio-forms";
import { Button, Grid, Icon, Popup, Header } from "semantic-ui-react";
import PropTypes from "prop-types";
import OrganizationsList from "../../organizations/OrganizationsList";

export const CommunityItemMobile = ({ result, index }) => {
  const communityType = result.ui?.type?.title_l10n;
  const canUpdate = result.ui.permissions.can_update;
  return (
    <Grid className="mobile only item community-item">
      {result.access.visibility === "restricted" && (
        <Grid.Row>
          <Grid.Column width={16} verticalAlign="middle" className="pl-0 pr-0">
            <RestrictedLabel access={result.access.visibility} />
          </Grid.Column>
        </Grid.Row>
      )}

      <Grid.Row>
        <Grid.Column
          width={(canUpdate && 11) || 16}
          verticalAlign="middle"
          className="pl-0 pr-0"
        >
          <div className="flex align-items-center">
            <Image
              wrapped
              src={result.links.logo}
              size="mini"
              className="community-image rel-mr-1"
              alt=""
            />
            <div>
              <Header as="a" className="ui medium header" href={result.links.self_html}>
                {result.metadata.title}
                {/* Show the icon for subcommunities */}
                {result.parent && (
                  <p className="ml-5 display-inline-block">
                    <Popup
                      content="Verified community"
                      trigger={
                        <Icon size="small" color="green" name="check circle outline" />
                      }
                      position="top center"
                    />
                  </p>
                )}
              </Header>
            </div>
          </div>
        </Grid.Column>

        {canUpdate && (
          <Grid.Column
            width={5}
            verticalAlign="middle"
            textAlign="right"
            className="pr-0"
          >
            <Button
              compact
              size="tiny"
              href={result.links.settings_html}
              className="mt-0 mr-0"
              labelPosition="left"
              icon="edit"
              content={i18next.t("Edit")}
            />
          </Grid.Column>
        )}
      </Grid.Row>

      {result.metadata.description && (
        <Grid.Row className="pt-0">
          <Grid.Column width={16} className="pl-0 pr-0">
            <p className="truncate-lines-1 text size small text-muted mt-5">
              {result.metadata.description}
            </p>
          </Grid.Column>
        </Grid.Row>
      )}
      {result.parent && (
        <div className="pl-0 sub header">
          {i18next.t("Part of")}{" "}
          <a href={`/communities/${result.parent.slug}`}>
            {result.parent.metadata.title}
          </a>
        </div>
      )}

      {(communityType || result.metadata.website || result.metadata.organizations) && (
        <Grid.Row className="pt-0">
          <Grid.Column width={16} verticalAlign="bottom" className="pl-0 pr-0">
            <div className="text size small text-muted">
              {communityType && (
                <div className="mb-5">
                  <CommunityTypeLabel transparent type={communityType} />
                </div>
              )}

              {result.metadata.website && (
                <div className="rel-mr-1 mb-5">
                  <Icon name="linkify" />
                  <a
                    href={result.metadata.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted"
                  >
                    {result.metadata.website}
                  </a>
                </div>
              )}

              {result.metadata.organizations && (
                <OrganizationsList organizations={result.metadata.organizations} />
              )}
            </div>
          </Grid.Column>
        </Grid.Row>
      )}
    </Grid>
  );
};

CommunityItemMobile.propTypes = {
  result: PropTypes.object.isRequired,
  index: PropTypes.string,
};

CommunityItemMobile.defaultProps = {
  index: null,
};
