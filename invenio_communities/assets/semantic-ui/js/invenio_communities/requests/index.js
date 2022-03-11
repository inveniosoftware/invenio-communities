/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import ReactDOM from "react-dom";
import _camelCase from "lodash/camelCase";
import { overrideStore } from "react-overridable";
import { SearchApp } from "@js/invenio_search_ui/components";
import { defaultComponents as RequestsDefaultComponents } from "./requests";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);

const getConfigFromDataAttribute = (element, attr) => {
  const dataValue = domContainer.dataset[attr];

  return JSON.parse(dataValue);
};

class CommunityRequests extends Component {
  constructor(props) {
    super(props);

    const { appId, ...config } = getConfigFromDataAttribute(
      domContainer,
      _camelCase("invenio-config")
    );
    this.appId = appId;
    this.config = config;

    for (const [componentId, component] of Object.entries(
      RequestsDefaultComponents(appId)
    )) {
      overrideStore.add(componentId, component);
    }
  }

  render() {
    return (
      <SearchApp appName={this.appId} key={this.appId} config={this.config} />
    );
  }
}

ReactDOM.render(<CommunityRequests community={community} />, domContainer);
export default CommunityRequests;
