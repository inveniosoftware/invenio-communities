// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { i18next } from "@translations/invenio_communities/i18next";
import CollectionTreeCardGroup from "./CollectionTreeCardGroup";

/**
 * CollectionTrees component
 * Renders a list of collection trees associated with a community
 * @component
 * @param {object} props - component props
 * @param {object} props.community - community data
 * @param {object} props.permissions - permissions data
 * @returns {JSX.Element} - rendered component
 */
class CollectionTrees extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    const { community } = this.props;

    return (
      <Overridable id="CollectionTrees" {...this.props}>
        <CollectionTreeCardGroup
          community={community}
          emptyMessage={i18next.t("There are no collection trees.")}
        />
      </Overridable>
    );
  }
}

CollectionTrees.propTypes = {
  community: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
};

export default CollectionTrees;
