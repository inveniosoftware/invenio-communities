// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import { CommunityTypeLabel } from "../labels";
import { RestrictedLabel } from "../labels";
import _truncate from "lodash/truncate";
import React from "react";
import { Image, InvenioPopup } from "react-invenio-forms";
import { Icon } from "semantic-ui-react";
import PropTypes from "prop-types";

export const CommunityCompactItemMobile = ({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
}) => {
  const communityType = result.ui?.type?.title_l10n;
  const { metadata, ui, links, access, id } = result;
  return (
    <div key={id} className={`community-item mobile only ${itemClassName}`}>
      <div className="display-grid auto-column-grid no-wrap">
        <div className="flex align-items-center">
          <Image
            wrapped
            size="mini"
            src={links.logo}
            alt=""
            className="community-image rel-mr-1"
          />

          <div>
            <a href={links.self_html} className="ui small header truncate-lines-2">
              {metadata.title}
            </a>
          </div>
        </div>

        <div className="flex align-items-center justify-end">
          {showPermissionLabel && (
            <span className="rel-mr-1">
              {ui?.permissions?.can_include_directly && (
                <InvenioPopup
                  popupId="direct-publish-info-popup"
                  size="small"
                  trigger={<Icon name="paper plane outline neutral" size="large" />}
                  ariaLabel={i18next.t("Submission information")}
                  content={i18next.t(
                    "Submission to this community does not require review, and will be published immediately."
                  )}
                />
              )}
            </span>
          )}
          {actions}
        </div>
      </div>

      <div className="full-width">
        {metadata.description && (
          <p
            className="truncate-lines-1 text size small text-muted mt-5 rel-mb-1"
            dangerouslySetInnerHTML={{
              __html: _truncate(metadata.description, { length: 50 }),
            }}
          />
        )}

        {(result.access.visibility === "restricted" ||
          communityType ||
          extraLabels) && (
          <div className="rel-mt-1">
            <RestrictedLabel access={access.visibility} />
            <CommunityTypeLabel type={communityType} />
            {extraLabels}
          </div>
        )}
      </div>
    </div>
  );
};

CommunityCompactItemMobile.propTypes = {
  result: PropTypes.object.isRequired,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
  actions: PropTypes.node,
};

CommunityCompactItemMobile.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
};
