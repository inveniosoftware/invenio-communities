// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import _get from "lodash/get";
import _truncate from "lodash/truncate";
import React from "react";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
import { Icon, Item } from "semantic-ui-react";
import { RightBottomLabel } from "./RightBottomLabel";

export const MobileRequestsItems = ({
  result,
  community,
  differenceInDays,
  isCreatorCommunity,
  creatorName,
  updateQueryState,
  currentQueryState,
}) => {
  const refreshAfterAction = () => {
    updateQueryState(currentQueryState);
  };

  return (
    <Item key={community.id} className="community-item mobile only flex">
      <Item.Content>
        <Item.Extra>
          {result.type && <RequestTypeLabel type={result.type} />}
          {result.status && result.is_closed && (
            <RequestStatusLabel status={result.status} />
          )}
        </Item.Extra>
        <Item.Header className="truncate-lines-2">
          <a
            className="header-link"
            href={`/communities/${community.slug}/requests/${result.id}`}
          >
            <Icon size="small" name="conversation" color="black" />
            {result.title}
          </a>
        </Item.Header>
        <Item.Meta>
          <small>
            {i18next.t(`Opened {{difference}} by`, {
              difference: differenceInDays,
            })}{" "}
            {isCreatorCommunity && (
              <Icon className="default-margin" name="users" />
            )}{" "}
            {creatorName}
          </small>
          <RightBottomLabel className="mb-5 block" result={result} />
          <div className="block">
            <RequestActionController
              request={result}
              actionSuccessCallback={refreshAfterAction}
            />
          </div>
        </Item.Meta>
      </Item.Content>
    </Item>
  );
};
