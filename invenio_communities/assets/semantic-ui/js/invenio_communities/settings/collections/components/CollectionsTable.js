// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Table, Grid, Button, Message, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";

const CollectionsTable = ({
  collections,
  collectionTreeTitle,
  onAddCollection,
  onAddChildCollection,
  onEditCollection,
  onDeleteCollection,
  collectionTreeId,
  collectionTreeSlug,
}) => {
  const renderCollectionRow = (item, key) => {
    const collection = item[key];

    return (
      <React.Fragment key={collection.id}>
        <Table.Row
          className={collection.depth > 0 ? "collection-depth-bg" : ""}
          data-depth={collection.depth}
        >
          <Table.Cell
            className="collection-depth-padding"
            data-depth={collection.depth}
          >
            {collection.depth > 0 && "↳"} {collection.title}
          </Table.Cell>
          <Table.Cell>{collection.slug}</Table.Cell>
          <Table.Cell>{collection.search_query}</Table.Cell>
          <Table.Cell>{collection.order}</Table.Cell>
          <Table.Cell>
            <Button
              positive
              compact
              size="mini"
              onClick={() => onAddChildCollection(collectionTreeSlug, collection.slug)}
            >
              {i18next.t("Add child")}
            </Button>
            <Button
              primary
              compact
              size="mini"
              onClick={() => onEditCollection(collectionTreeSlug, collection)}
            >
              {i18next.t("Edit")}
            </Button>
            <Button
              negative
              compact
              size="mini"
              onClick={() => onDeleteCollection(collectionTreeSlug, collection)}
            >
              {i18next.t("Delete")}
            </Button>
          </Table.Cell>
        </Table.Row>
        {collection.children.map((childKey) => renderCollectionRow(item, childKey))}
      </React.Fragment>
    );
  };

  if (!collections || Object.keys(collections).length === 0) {
    return (
      <Message info>
        <Message.Header>
          {i18next.t("No collections found for ")} "{collectionTreeTitle}"
        </Message.Header>
        <Message.Content className="rel-mt-2">
          <Button
            positive
            size="small"
            onClick={() => onAddCollection(collectionTreeId, collectionTreeSlug)}
          >
            <Icon name="plus" /> {i18next.t("New collection")}
          </Button>
        </Message.Content>
      </Message>
    );
  }

  return (
    <div className="rel-mt-2">
      <Grid>
        <Grid.Row>
          <Grid.Column width={12}>
            <h3>
              {i18next.t("Collections for")} "{collectionTreeTitle}"
            </h3>
          </Grid.Column>
          <Grid.Column width={4} textAlign="right">
            <Button
              positive
              size="small"
              onClick={() => onAddCollection(collectionTreeId, collectionTreeSlug)}
            >
              <Icon name="plus" /> {i18next.t("New collection")}
            </Button>
          </Grid.Column>
        </Grid.Row>
      </Grid>
      <Table celled>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>{i18next.t("Title")}</Table.HeaderCell>
            <Table.HeaderCell>{i18next.t("Slug")}</Table.HeaderCell>
            <Table.HeaderCell>{i18next.t("Search Query")}</Table.HeaderCell>
            <Table.HeaderCell>{i18next.t("Order")}</Table.HeaderCell>
            <Table.HeaderCell>{i18next.t("Actions")}</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {collections.map((collection) =>
            renderCollectionRow(collection, collection["root"])
          )}
        </Table.Body>
      </Table>
    </div>
  );
};

CollectionsTable.propTypes = {
  collections: PropTypes.object.isRequired,
  collectionTreeTitle: PropTypes.string.isRequired,
  onAddCollection: PropTypes.func.isRequired,
  onAddChildCollection: PropTypes.func.isRequired,
  onEditCollection: PropTypes.func.isRequired,
  onDeleteCollection: PropTypes.func.isRequired,
  collectionTreeId: PropTypes.string.isRequired,
  collectionTreeSlug: PropTypes.string.isRequired,
};

export default CollectionsTable;
