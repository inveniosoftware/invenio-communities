// This file is part of Invenio-Communities
// Copyright (C) 2026 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import {
  Grid,
  Header,
  Button,
  Icon,
  Divider,
  Container,
  Message,
} from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { CollectionsContext } from "../../../api/collections/CollectionsContextProvider";
import CollectionBrowseCard from "./CollectionBrowseCard";

class CollectionTreeBrowseView extends Component {
  static contextType = CollectionsContext;
  constructor(props) {
    super(props);
    this.state = {
      collectionMap: {},
      rootCollections: [],
      draggedIndex: null,
      draggedOverIndex: null,
    };
  }

  componentDidMount() {
    this.transformCollectionsForDisplay();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.collections !== this.props.collections) {
      this.transformCollectionsForDisplay();
    }
  }

  /**
   * Transform flat collection data structure into hierarchical format for display.
   * Recursively processes all collections and their descendants at any depth level,
   * building a complete collectionMap for rendering and a sorted array of root collections.
   */
  transformCollectionsForDisplay = () => {
    const { collections } = this.props;

    if (!collections || collections.length === 0) {
      this.setState({ collectionMap: {}, rootCollections: [] });
      return;
    }

    const collectionMap = {};
    const rootCollections = [];

    /**
     * Recursive helper to process a collection and all its descendants.
     * @param {string} slug - The collection slug to process
     * @param {Object} collectionData - The flat collection data object from API
     */
    const processCollectionAndDescendants = (slug, collectionData) => {
      const collection = collectionData[slug];
      if (!collection || collectionMap[slug]) return; // Skip if missing or already processed

      // Add to map
      collectionMap[slug] = {
        ...collection,
        children: collection.children || [],
        num_records: collection.num_records || 0,
      };

      // Recursively process all children
      if (collection.children && collection.children.length > 0) {
        collection.children.forEach((childSlug) => {
          processCollectionAndDescendants(childSlug, collectionData);
        });
      }
    };

    // Process each collection tree
    collections.forEach((collectionData) => {
      const rootSlug = collectionData.root;
      const rootCollection = collectionData[rootSlug];

      if (!collectionMap[rootSlug]) {
        // Recursively process root and ALL descendants
        processCollectionAndDescendants(rootSlug, collectionData);

        // Add to rootCollections if it's actually a root (depth 0)
        if (rootCollection && rootCollection.depth === 0) {
          rootCollections.push(collectionMap[rootSlug]);
        }
      }
    });

    // Sort root collections by order field
    rootCollections.sort((a, b) => (a.order || 0) - (b.order || 0));

    this.setState({ collectionMap, rootCollections });
  };

  handleEdit = (collection) => {
    const { onEditCollection, collectionTree } = this.props;
    onEditCollection(collectionTree.slug, collectionTree.title, collection);
  };

  handleDelete = (collection) => {
    const { onDeleteCollection, collectionTree } = this.props;
    onDeleteCollection(collectionTree.slug, collection);
  };

  handleAddChild = (collection) => {
    const { onAddChildCollection, collectionTree } = this.props;
    onAddChildCollection(collectionTree.slug, collectionTree.title, collection.slug, collection.title);
  };

  /**
   * Handle the start of dragging a root collection.
   * @param {DragEvent} e - The drag event
   * @param {number} index - Index of the root collection being dragged
   */
  handleDragStart = (e, index) => {
    this.setState({ draggedIndex: index });
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/html", e.currentTarget);
  };

  /**
   * Handle dragging over a root collection position.
   * @param {DragEvent} e - The drag event
   * @param {number} index - Index of the position being dragged over
   */
  handleDragOver = (e, index) => {
    // Only handle drag over if we're actually dragging a parent collection
    if (this.state.draggedIndex === null) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = "move";

    if (index !== this.state.draggedOverIndex) {
      this.setState({ draggedOverIndex: index });
    }
  };

  /**
   * Handle the end of dragging a root collection.
   * Performs optimistic UI update and persists order to backend.
   * Reverts on error.
   * @param {DragEvent} e - The drag event
   */
  handleDragEnd = async (e) => {
    e.stopPropagation();
    const { draggedIndex, draggedOverIndex, rootCollections } = this.state;
    const { collectionTree } = this.props;

    // Reset drag state
    this.setState({ draggedIndex: null, draggedOverIndex: null });

    if (
      draggedIndex === null ||
      draggedOverIndex === null ||
      draggedIndex === draggedOverIndex
    ) {
      return;
    }

    // Reorder array
    const items = Array.from(rootCollections);
    const [reorderedItem] = items.splice(draggedIndex, 1);
    items.splice(draggedOverIndex, 0, reorderedItem);

    // Optimistic UI update
    this.setState({ rootCollections: items });

    // Use batch endpoint for single API call
    if (this.context.api && collectionTree) {
      try {
        const orderPayload = {
          order: items.map((collection, index) => ({
            slug: collection.slug,
            order: (index + 1) * 10, // Use gaps (10, 20, 30...)
          })),
        };

        await this.context.api.batch_reorder_collections(
          collectionTree.slug,
          orderPayload
        );
      } catch (error) {
        console.error("Failed to update collection order:", error);
        // Revert on error
        this.setState({ rootCollections });
      }
    }
  };

  render() {
    const {
      collectionTree,
      onAddCollection,
      onEditTree,
      onDeleteTree,
      community,
      showHeader = false,
      maxCollectionDepth,
    } = this.props;
    const { collectionMap, rootCollections, draggedIndex, draggedOverIndex } =
      this.state;

    if (!collectionTree) {
      return null;
    }

    return (
      <Container className="rel-mt-2">
        {showHeader && (
          <>
            <Grid verticalAlign="middle" className="rel-mb-2">
              <Grid.Column width={10}>
                <Header as="h2">
                  {i18next.t("Collections for")} "{collectionTree.title}"
                </Header>
              </Grid.Column>
              <Grid.Column width={6} textAlign="right">
                <Button
                  positive
                  onClick={() =>
                    onAddCollection(collectionTree.id, collectionTree.slug, collectionTree.title)
                  }
                >
                  <Icon name="plus" /> {i18next.t("New collection")}
                </Button>
                <Button onClick={() => onEditTree(collectionTree)}>
                  <Icon name="edit" /> {i18next.t("Edit Category")}
                </Button>
                <Button negative onClick={() => onDeleteTree(collectionTree)}>
                  <Icon name="trash" /> {i18next.t("Delete Category")}
                </Button>
              </Grid.Column>
            </Grid>
            <Divider />
          </>
        )}

        {rootCollections.length === 0 ? (
          <Message info>
            <Message.Header>
              {i18next.t("No collections found for")} "{collectionTree.title}"
            </Message.Header>
            <Message.Content className="rel-mt-2">
              <Button
                positive
                size="small"
                onClick={() => onAddCollection(collectionTree.id, collectionTree.slug, collectionTree.title)}
              >
                <Icon name="plus" /> {i18next.t("New collection")}
              </Button>
            </Message.Content>
          </Message>
        ) : (
          <Grid relaxed stackable>
            {rootCollections.map((collection, index) => {
              const isCollectionDragging = draggedIndex === index;
              const isCollectionDraggedOver =
                draggedOverIndex === index && draggedIndex !== index;

              return (
                <Grid.Column
                  width={4}
                  key={collection.slug}
                  className={`collection-grid-column collection-card ${
                    isCollectionDragging ? "dragging" : ""
                  } ${isCollectionDraggedOver ? "drag-over" : ""}`}
                  onDragOver={(e) => this.handleDragOver(e, index)}
                >
                  <CollectionBrowseCard
                    collection={collection}
                    allCollections={collectionMap}
                    onEdit={this.handleEdit}
                    onDelete={this.handleDelete}
                    onAddChild={this.handleAddChild}
                    community={community}
                    collectionApi={this.context.api}
                    treeSlug={collectionTree.slug}
                    isDraggable
                    dragIndex={index}
                    onDragStart={this.handleDragStart}
                    onDragEnd={this.handleDragEnd}
                    isDragging={draggedIndex === index}
                    maxCollectionDepth={maxCollectionDepth}
                  />
                </Grid.Column>
              );
            })}
          </Grid>
        )}
      </Container>
    );
  }
}

CollectionTreeBrowseView.propTypes = {
  collectionTree: PropTypes.shape({
    id: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    collections: PropTypes.array,
  }).isRequired,
  collections: PropTypes.array.isRequired,
  onAddCollection: PropTypes.func.isRequired,
  onAddChildCollection: PropTypes.func.isRequired,
  onEditCollection: PropTypes.func.isRequired,
  onDeleteCollection: PropTypes.func.isRequired,
  onEditTree: PropTypes.func.isRequired,
  onDeleteTree: PropTypes.func.isRequired,
  community: PropTypes.object,
  showHeader: PropTypes.bool,
  maxCollectionDepth: PropTypes.number.isRequired,
};

export default CollectionTreeBrowseView;
