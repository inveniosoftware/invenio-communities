/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { parametrize } from "react-overridable";
import { Icon } from "semantic-ui-react";
import {
  LabelTypeSubmission,
  LabelTypeInvitation,
  LabelStatusSubmit,
  LabelStatusDelete,
  LabelStatusAccept,
  LabelStatusDecline,
  LabelStatusCancel,
  LabelStatusExpire,
} from "@js/invenio_requests/request";
import {
  BucketAggregationElement,
  RecordFacetsValues,
  RecordSearchBarElement,
  RequestsEmptyResultsWithState,
  RequestsFacets,
  RequestsResults,
  RequestsResultsGridItemTemplate,
  RequestsResultsItemTemplateCommunity,
  RequestsSearchLayout,
} from "./requests";
import {
  RequestAcceptButton,
  RequestCancelButton,
  RequestDeclineButton,
  RequestCancelButtonModal,
} from "@js/invenio_requests/components/Buttons";

const domContainer = document.getElementById("communities-request-search-root");

const community = JSON.parse(domContainer.dataset.community);

const RequestsResultsGridItemTemplateWithCommunity = parametrize(
  RequestsResultsGridItemTemplate,
  {
    community: community,
  }
);

const RequestsResultsItemTemplateWithCommunity = parametrize(
  RequestsResultsItemTemplateCommunity,
  {
    community: community,
  }
);
const RequestAcceptButtonWithConfig = parametrize(RequestAcceptButton, {
  size: "mini",
  className: "ml-5"
});

const RequestDeclineButtonWithConfig = parametrize(RequestDeclineButton, {
  size: "mini",
  className: "ml-5"
});

const RequestCancelButtonWithConfig = parametrize(RequestCancelButton, {
  size: "mini",
  className: "ml-5"
});

const RequestAcceptButtonMobileWithConfig = parametrize(RequestAcceptButton, {
  size: "mini",
  className: "mt-10 fluid-responsive",
});

const RequestDeclineButtonMobileWithConfig = parametrize(RequestDeclineButton, {
  size: "mini",
  className: "mt-10 fluid-responsive",
});

const RequestCancelButtonMobileWithConfig = parametrize(RequestCancelButton, {
  size: "mini",
  className: "mt-10 fluid-responsive",
});

const CommunitySubmission = () => (
  <LabelTypeSubmission className="rel-mr-1 primary" size="small" />
)

const CommunityInvitation = () => (
  <LabelTypeInvitation className="rel-mr-1 primary" size="small" />
)

const Submitted = () => (
  <LabelStatusSubmit className="rel-mr-1 primary" size="small" />
)

const Deleted = () => (
  <LabelStatusDelete className="rel-mr-1 negative" size="small" />
)

const Accepted = () => (
  <LabelStatusAccept className="rel-mr-1 positive" size="small" />
)

const Declined = () => (
  <LabelStatusDecline className="rel-mr-1 negative" size="small" />
)

const Cancelled = () => (
  <LabelStatusCancel className="rel-mr-1 neutral" size="small" />
)

const Expired = () => (
  <LabelStatusExpire className="rel-mr-1 expired" size="small" />
)

const defaultComponents = {
  "BucketAggregation.element": BucketAggregationElement,
  "BucketAggregationValues.element": RecordFacetsValues,
  "SearchApp.facets": RequestsFacets,
  "ResultsList.item": RequestsResultsItemTemplateWithCommunity,
  "ResultsGrid.item": RequestsResultsGridItemTemplateWithCommunity,
  "SearchApp.layout": RequestsSearchLayout,
  "SearchApp.results": RequestsResults,
  "SearchBar.element": RecordSearchBarElement,
  "EmptyResults.element": RequestsEmptyResultsWithState,
  "RequestTypeLabel.layout.community-submission": CommunitySubmission,
  "RequestTypeLabel.layout.community-invitation": CommunityInvitation,
  "RequestStatusLabel.layout.submitted": Submitted,
  "RequestStatusLabel.layout.deleted": Deleted,
  "RequestStatusLabel.layout.accepted": Accepted,
  "RequestStatusLabel.layout.declined": Declined,
  "RequestStatusLabel.layout.cancelled": Cancelled,
  "RequestStatusLabel.layout.expired": Expired,
  "RequestActionModalTrigger.accept.computer-tablet": RequestAcceptButtonWithConfig,
  "RequestActionModalTrigger.decline.computer-tablet": RequestDeclineButtonWithConfig,
  "RequestActionModalTrigger.cancel.computer-tablet": RequestCancelButtonWithConfig,
  "RequestActionModalTrigger.accept.mobile": RequestAcceptButtonMobileWithConfig,
  "RequestActionModalTrigger.decline.mobile": RequestDeclineButtonMobileWithConfig,
  "RequestActionModalTrigger.cancel.mobile": RequestCancelButtonMobileWithConfig,
  "RequestActionButton.cancel": RequestCancelButtonModal,
  "RequestActionButton.decline": RequestDeclineButton,
  "RequestActionButton.accept": RequestAcceptButton,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
