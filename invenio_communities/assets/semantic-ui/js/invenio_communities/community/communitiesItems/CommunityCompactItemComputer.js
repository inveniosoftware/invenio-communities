// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// InvenioRDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import PropTypes from "prop-types";
import _truncate from "lodash/truncate";

import { Image, InvenioPopup } from "react-invenio-forms";
import { Item, Grid, Icon } from "semantic-ui-react";
import { CommunityTypeLabel, RestrictedLabel } from "../labels";

export const CommunityCompactItemComputer = ({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
}) => {
  const { metadata, ui, links, access, id } = result;
  const communityType = ui?.type?.title_l10n;

  return (
    <Item
      key={id}
      className={`computer tablet only justify-space-between community-item ${itemClassName}`}
    >
      <Image size="tiny" src={links.logo} alt="" />
      <Grid>
        <Grid.Column width={10}>
          <Item.Content verticalAlign="middle">
            <Item.Header
              as="a"
              href={links.self_html}
              className="ui small header flex align-items-center mb-5"
            >
              {metadata.title}
            </Item.Header>

            {metadata.description && (
              <Item.Description
                as="p"
                dangerouslySetInnerHTML={{
                  __html: _truncate(metadata.description, { length: 50 }),
                }}
              />
            )}
            <Item.Extra>
              <RestrictedLabel access={access.visibility} />
              <CommunityTypeLabel type={communityType} />
              {extraLabels}
            </Item.Extra>
          </Item.Content>
        </Grid.Column>
        <Grid.Column width={5} verticalAlign="middle" align="right">
          {showPermissionLabel && (
            <Item.Content>
              <Item.Meta>
                {ui?.permissions?.can_include_directly && (
                  <InvenioPopup
                    popupId="direct-publish-info-popup"
                    size="small"
                    trigger={<Icon name="paper plane outline" size="large" />}
                    ariaLabel={i18next.t("Submission information")}
                    content={i18next.t(
                      "Submission to this community does not require review, and will be published immediately."
                    )}
                  />
                )}
                {!ui?.permissions?.can_include_directly && (
                  <InvenioPopup
                    popupId="requires-review-popup"
                    size="small"
                    ariaLabel={i18next.t("Submission information")}
                    trigger={
                      <span>
                        <Icon name="comments outline" size="large" />
                        <Icon corner="top right" name="question" size="small" fitted />
                      </span>
                    }
                    content={i18next.t(
                      "Submission to this community requires review and will be published upon curator's approval."
                    )}
                  />
                )}
              </Item.Meta>
            </Item.Content>
          )}
        </Grid.Column>
      </Grid>
      <div className="flex align-items-center">{actions}</div>
    </Item>
  );
};

CommunityCompactItemComputer.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
};

CommunityCompactItemComputer.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
};
