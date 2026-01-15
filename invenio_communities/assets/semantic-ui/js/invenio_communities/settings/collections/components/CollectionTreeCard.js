// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _truncate from "lodash/truncate";
import React from "react";
import PropTypes from "prop-types";
import { Button, Card } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";

const CollectionTreeCard = ({
  collectionTree,
  onViewClick,
  onEditClick,
  onDeleteClick,
  isSelected,
  onError,
}) => {
  return (
    <Card fluid>
      <Card.Content>
        <Card.Header>{_truncate(collectionTree.title, { length: 30 })}</Card.Header>
        {collectionTree.slug && (
          <Card.Description>
            <div className="truncate-lines-2">{collectionTree.slug}</div>
            <Button
              primary
              compact
              size="small"
              onClick={() => onEditClick(collectionTree)}
              id="edit-collection-tree-button"
            >
              {i18next.t("Edit")}
            </Button>
            <Button
              secondary
              compact
              size="small"
              onClick={() => onViewClick(collectionTree.id)}
              active={isSelected}
            >
              {isSelected ? i18next.t("Hide") : i18next.t("View")}
            </Button>
            <Button
              negative
              compact
              size="small"
              onClick={() => onDeleteClick(collectionTree)}
            >
              {i18next.t("Delete")}
            </Button>
          </Card.Description>
        )}
      </Card.Content>
    </Card>
  );
};

CollectionTreeCard.propTypes = {
  collectionTree: PropTypes.object.isRequired,
  onViewClick: PropTypes.func.isRequired,
  onEditClick: PropTypes.func.isRequired,
  onDeleteClick: PropTypes.func.isRequired,
  isSelected: PropTypes.bool,
  onError: PropTypes.func.isRequired,
};

export default CollectionTreeCard;
