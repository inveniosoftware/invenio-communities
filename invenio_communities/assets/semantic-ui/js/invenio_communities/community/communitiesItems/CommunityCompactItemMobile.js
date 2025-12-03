// This file is part of InvenioRDM
// Copyright (C) 2022-2024 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_communities/i18next";
import { RestrictedLabel } from "../labels";
import _truncate from "lodash/truncate";
import React from "react";
import { Image, InvenioPopup } from "react-invenio-forms";
import { Icon, Label, Popup } from "semantic-ui-react";
import PropTypes from "prop-types";

export const CommunityCompactItemMobile = ({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
  detailUrl,
  isCommunityDefault,
  recordRequests,
}) => {
  const { metadata, ui, links, access, id } = result;
  const viewComments = id in recordRequests;
  return (
    <div
      key={id}
      className={`community-item mobile only align-items-start ${itemClassName}`}
    >
      <div className="display-grid auto-column-grid no-wrap">
        <div className="flex align-items-center">
          <Image
            wrapped
            size="mini"
            src={links.logo}
            alt=""
            className="community-image rel-mr-1"
          />

          <div className="flex align-items-center rel-mb-1">
            <a
              href={detailUrl || links.self_html}
              className="ui small header truncate-lines-2 m-0 mr-5"
              target="_blank"
              rel="noreferrer"
              aria-label={`${metadata.title} (${i18next.t("opens in new tab")})`}
            >
              {metadata.title}
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
            </a>
            <i className="small icon external primary" aria-hidden="true" />
            {(result.access.visibility === "restricted" || extraLabels) && (
              <>
                <RestrictedLabel access={access.visibility} />
                {extraLabels}
              </>
            )}
            {isCommunityDefault && (
              <Label color="purple" size="tiny">
                <Icon name="paint brush" />
                {i18next.t("Branding")}
              </Label>
            )}
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
          <p className="truncate-lines-1 text size small text-muted mt-5 rel-mb-1">
            {_truncate(metadata.description, { length: 50 })}
          </p>
        )}
        {viewComments && (
          <div className="mt-10">
            <small>
              <b>
                <a
                  // building request link as the self_html of the request is
                  // /requests/<uuid> which doesn't resolve as missing
                  // /communities/ or /me/. We prefer /communities/ here
                  href={`${links.self_html}requests/${recordRequests[id]}`}
                >
                  <Icon name="discussions" className="mr-5" />
                  {i18next.t("View comments")}
                </a>
              </b>
            </small>
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
  detailUrl: PropTypes.string,
  isCommunityDefault: PropTypes.bool.isRequired,
  recordRequests: PropTypes.object,
};

CommunityCompactItemMobile.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
  detailUrl: undefined,
  recordRequests: {},
};
