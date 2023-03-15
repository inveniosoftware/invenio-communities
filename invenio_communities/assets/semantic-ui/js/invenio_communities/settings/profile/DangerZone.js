/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2023 CERN.
 * Copyright (C) 2021-2022 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import { Grid, Header, Segment } from "semantic-ui-react";
import { CommunityApi } from "../../api";
import { DeleteButton } from "./DeleteButton";
import { RenameCommunitySlugButton } from "./RenameCommunitySlugButton";
import PropTypes from "prop-types";

const DangerZone = ({ community, onError }) => (
  <Segment className="negative rel-mt-2">
    <Header as="h2" className="negative">
      {i18next.t("Danger zone")}
    </Header>
    <Grid>
      <Grid.Column mobile={16} tablet={10} computer={12}>
        <Header as="h3" size="small">
          {i18next.t("Change identifier")}
        </Header>
        <p>
          {i18next.t(
            "Changing your community's unique identifier can have unintended side effects."
          )}
        </p>
      </Grid.Column>
      <Grid.Column mobile={16} tablet={6} computer={4} floated="right">
        <RenameCommunitySlugButton community={community} onError={onError} />
      </Grid.Column>
      <Grid.Column mobile={16} tablet={10} computer={12} floated="left">
        <Header as="h3" size="small">
          {i18next.t("Delete community")}
        </Header>
        <p>{i18next.t("Once deleted, it will be gone forever. Please be certain.")}</p>
      </Grid.Column>
      <Grid.Column mobile={16} tablet={6} computer={4} floated="right">
        <DeleteButton
          community={community}
          label={i18next.t("Delete community")}
          redirectURL="/communities"
          confirmationMessage={
            <Header as="h3">
              {i18next.t("Are you sure you want to delete this community?")}
            </Header>
          }
          onDelete={async () => {
            const client = new CommunityApi();
            await client.delete(community.id);
          }}
          onError={onError}
        />
      </Grid.Column>
    </Grid>
  </Segment>
);

DangerZone.propTypes = {
  community: PropTypes.object.isRequired,
  onError: PropTypes.func.isRequired,
};

export default DangerZone;
