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

export const CommunityItemComputer = ({ result }) => {
  const communityType = result.ui?.type?.title_l10n;
  const canUpdate = result.ui?.permissions?.can_update;

  return (
    <Grid className="computer tablet only item community-item">
      <Grid.Column
        tablet={(canUpdate && 13) || 16}
        computer={13}
        verticalAlign="middle"
        className="pl-0"
      >
        <div className="flex align-items-center">
          <Image
            wrapped
            src={result.links.logo}
            size="tiny"
            className="community-image rel-mr-2"
            alt=""
          />
          <div>
            {result.access.visibility === "restricted" && (
              <div className="rel-mb-1">
                <RestrictedLabel access={result.access.visibility} />
              </div>
            )}
            <Header as="a" className="ui medium header" href={result.links.self_html}>
              {result.metadata.title}
              {/* Show the icon for subcommunities */}
              {result.parent && (
                <p className="ml-5 display-inline-block">
                  <Popup
                    content={i18next.t("Verified community")}
                    trigger={
                      <Icon size="small" color="green" name="check circle outline" />
                    }
                    position="top center"
                  />
                </p>
              )}
            </Header>
            {result.metadata.description && (
              <p className="truncate-lines-1 text size small text-muted mt-5">
                {result.metadata.description}
              </p>
            )}
            {result.parent && (
              <div className="sub header">
                {i18next.t("Part of")}{" "}
                <a href={`/communities/${result.parent.slug}`}>
                  {result.parent.metadata.title}
                </a>
              </div>
            )}

            {(communityType ||
              result.metadata.website ||
              result.metadata.organizations) && (
              <div className="flex align-items-center wrap mt-5 text size small text-muted">
                {communityType && (
                  <CommunityTypeLabel transparent type={communityType} />
                )}

                {result.metadata.website && (
                  <div className="rel-mr-1">
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
            )}
          </div>
        </div>
      </Grid.Column>

      {canUpdate && (
        <Grid.Column width={3} textAlign="right" className="pr-0">
          <div>
            <Button
              compact
              size="small"
              href={result.links.settings_html}
              className="mt-0 mr-0"
              labelPosition="left"
              icon="edit"
              content={i18next.t("Edit")}
            />
          </div>
        </Grid.Column>
      )}
    </Grid>
  );
};

CommunityItemComputer.propTypes = {
  result: PropTypes.object.isRequired,
};
