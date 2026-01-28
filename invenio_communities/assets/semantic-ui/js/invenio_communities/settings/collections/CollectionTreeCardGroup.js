/*
 * This file is part of Invenio-Communities.
 * Copyright (C) 2024-2025 CERN.
 *
 * Invenio-Communities is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { withCancel } from "react-invenio-forms";
import { Button, Grid, Icon, Modal, Header } from "semantic-ui-react";
import { communityErrorSerializer } from "../../api/serializers";
import { CollectionsContext } from "../../api/collections/CollectionsContextProvider";
import CollectionTreeBrowseView from "./components/CollectionTreeBrowseView";
import PlaceholderLoader from "./components/PlaceholderLoader";
import EmptyMessage from "./components/EmptyMessage";
import NewCollectionTreeForm from "./forms/NewCollectionTreeForm";
import UpdateCollectionTreeForm from "./forms/UpdateCollectionTreeForm";
import NewCollectionForm from "./forms/NewCollectionForm";
import NewChildCollectionForm from "./forms/NewChildCollectionForm";
import UpdateCollectionForm from "./forms/UpdateCollectionForm";
import DeleteCollectionAction from "./actions/DeleteCollectionAction";
import DeleteCollectionTreeAction from "./actions/DeleteCollectionTreeAction";

class CollectionTreeCardGroup extends Component {
  static contextType = CollectionsContext;

  constructor(props) {
    super(props);
    this.state = {
      isLoading: false,
      error: null,
      data: {},
      expandedTrees: {},
      showCollectionTreeFormModal: false,
      showCollectionFormModal: false,
      selectedTreeSlug: null,
      showEditModal: false,
      showDeleteModal: false,
      treeToEdit: null,
      showChildCollectionModal: false,
      showEditCollectionFormModel: false,
      showDeleteCollectionFormModel: false,
      parentCollectionSlug: null,
      parentCollectionQuery: null,
      collectionToDelete: null,
      draggedTreeIndex: null,
      draggedOverTreeIndex: null,
    };
  }
  // Open the modal
  openCollectionTreeFormModal = () => {
    this.setState({
      showCollectionTreeFormModal: true,
    });
  };

  // Close the modal
  closeCollectionTreeFormModal = () => {
    this.setState({
      showCollectionTreeFormModal: false,
    });
  };

  // Handle success
  handleCollectionTreeFormSuccess = () => {
    this.closeCollectionTreeFormModal();
    this.fetchData(); // Refresh the data
  };

  openChildCollectionModal = (treeSlug, parentSlug) => {
    // Find the parent collection to get its query
    const collectionTrees = Object.values(this.state.data);
    const tree = collectionTrees.find((t) => t.slug === treeSlug);
    let parentCollection = null;

    if (tree) {
      // Search for the parent collection recursively
      const findCollection = (collections, slug) => {
        for (const col of collections) {
          if (col.slug === slug) return col;
          if (col.children && col.children.length > 0) {
            const found = findCollection(col.children, slug);
            if (found) return found;
          }
        }
        return null;
      };
      parentCollection = findCollection(tree.collections, parentSlug);
    }

    // Defensive check: prevent creating children for collections at or above max depth
    const { maxCollectionDepth } = this.props;
    if (parentCollection && parentCollection.depth >= maxCollectionDepth) {
      console.warn(
        `Cannot add child to collection at depth ${parentCollection.depth}. Maximum allowed depth is ${maxCollectionDepth}.`
      );
      return;
    }

    const parentQuery = parentCollection ? parentCollection.search_query : null;

    this.setState({
      showChildCollectionModal: true,
      selectedTreeSlug: treeSlug,
      parentCollectionSlug: parentSlug,
      parentCollectionQuery: parentQuery,
    });
  };

  // Close the modal
  closeChildCollectionModal = () => {
    this.setState({
      showChildCollectionModal: false,
      parentCollectionSlug: null,
      parentCollectionQuery: null,
      selectedTreeSlug: null,
    });
  };

  // Handle success
  handleChildCollectionSuccess = () => {
    this.closeChildCollectionModal();
    this.fetchData(); // Refresh the data
  };

  // Open the edit modal
  openEditModal = (tree) => {
    this.setState({
      showEditModal: true,
      treeToEdit: tree,
    });
  };

  // Close the edit modal
  closeEditModal = () => {
    this.setState({
      showEditModal: false,
      treeToEdit: null,
    });
  };

  // Handle success after editing
  handleEditSuccess = () => {
    this.closeEditModal();
    this.fetchData(); // Refresh the collection trees
  };

  // Open the delete modal
  openDeleteModal = (tree) => {
    this.setState({
      showDeleteModal: true,
      treeToEdit: tree,
    });
  };

  // Close the delete modal
  closeDeleteModal = () => {
    this.setState({
      showDeleteModal: false,
      treeToEdit: null,
    });
  };

  // Handle success after deleting
  handleDeleteSuccess = () => {
    this.closeDeleteModal();
    this.fetchData(); // Refresh the collection trees
  };

  // Handle expand/collapse of collection tree
  toggleTreeExpansion = (treeId) => {
    this.setState((prevState) => ({
      expandedTrees: {
        ...prevState.expandedTrees,
        [treeId]: !prevState.expandedTrees[treeId],
      },
    }));
  };

  /**
   * Handle the start of dragging a collection tree.
   * @param {DragEvent} e - The drag event
   * @param {number} index - Index of the tree being dragged
   */
  handleTreeDragStart = (e, index) => {
    this.setState({ draggedTreeIndex: index });
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/html", e.currentTarget);
  };

  /**
   * Handle dragging over a collection tree position.
   * @param {DragEvent} e - The drag event
   * @param {number} index - Index of the position being dragged over
   */
  handleTreeDragOver = (e, index) => {
    if (this.state.draggedTreeIndex === null) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = "move";

    if (index !== this.state.draggedOverTreeIndex) {
      this.setState({ draggedOverTreeIndex: index });
    }
  };

  /**
   * Handle the end of dragging a collection tree.
   * Performs UI update with order field updates,
   * persists to backend, and reverts on error.
   * @param {DragEvent} e - The drag event
   */
  handleTreeDragEnd = async (e) => {
    e.stopPropagation();
    const { draggedTreeIndex, draggedOverTreeIndex, data } = this.state;

    // Reset drag state
    this.setState({ draggedTreeIndex: null, draggedOverTreeIndex: null });

    if (
      draggedTreeIndex === null ||
      draggedOverTreeIndex === null ||
      draggedTreeIndex === draggedOverTreeIndex
    ) {
      return;
    }

    // Get trees as array and sort by order field (must match render order!)
    const trees = Object.values(data).sort((a, b) => (a.order || 0) - (b.order || 0));

    // Reorder array
    const [reorderedTree] = trees.splice(draggedTreeIndex, 1);
    trees.splice(draggedOverTreeIndex, 0, reorderedTree);

    // Update order field for each tree and convert back to object format
    const reorderedData = {};
    trees.forEach((tree, index) => {
      const updatedTree = {
        ...tree,
        order: (index + 1) * 10,
      };
      reorderedData[tree.slug] = updatedTree;
    });

    this.setState({ data: reorderedData });

    // Persist to backend
    try {
      const orderPayload = {
        order: trees.map((tree, index) => ({
          slug: tree.slug,
          order: (index + 1) * 10,
        })),
      };

      await this.context.api.batch_reorder_trees(orderPayload);
    } catch (error) {
      console.error("Failed to update tree order:", error);
      // Revert on error
      this.setState({ data });
    }
  };

  openCollectionFormModal = (treeId, treeSlug) => {
    this.setState({
      showCollectionFormModal: true,
      selectedTreeSlug: treeSlug,
    });
  };

  closeCollectionFormModal = () => {
    this.setState({ showCollectionFormModal: false });
  };

  handleCollectionFormSuccess = () => {
    this.closeCollectionFormModal();
    this.fetchData();
  };

  openEditCollectionFormModal = (treeSlug, collection) => {
    // Find the parent collection in the tree to get its query
    const collectionTrees = Object.values(this.state.data);
    const tree = collectionTrees.find((t) => t.slug === treeSlug);
    const parentCollection = tree
      ? this.findParentCollection(tree.collections, collection.slug)
      : null;
    const parentQuery = parentCollection ? parentCollection.search_query : null;

    this.setState({
      showEditCollectionFormModel: true,
      selectedTreeSlug: treeSlug,
      selectedCollectionSlug: collection.slug,
      collectionData: collection,
      parentCollectionQuery: parentQuery,
    });
  };

  // Close the modal
  closeEditCollectionFormModal = () => {
    this.setState({
      showEditCollectionFormModel: false,
      selectedCollectionSlug: null,
      selectedTreeSlug: null,
      collectionData: null,
      parentCollectionQuery: null,
    });
  };

  handleEditCollectionFormSuccess = () => {
    this.closeEditCollectionFormModal();
    this.fetchData();
  };

  // Helper function to find parent collection based on depth
  // Collections structure: array of objects where each object has numeric keys (collection IDs)
  // Parent collections have depth: 0, children have depth: 1, etc.
  findParentCollection = (collections, targetSlug) => {
    // Iterate through each collection tree group
    for (const collectionGroup of collections) {
      // Convert the object to an array of collections
      const collectionsArray = Object.values(collectionGroup).filter(
        (item) => typeof item === "object" && item !== null && item.slug
      );

      // Find the target collection
      const targetCollection = collectionsArray.find((col) => col.slug === targetSlug);

      if (targetCollection) {
        // If target is depth 0, it has no parent (root collection)
        if (targetCollection.depth === 0) {
          return null;
        }

        // Find parent: collection with depth one less than target
        const parentDepth = targetCollection.depth - 1;
        const parent = collectionsArray.find((col) => col.depth === parentDepth);

        return parent || null;
      }
    }

    return null;
  };

  openDeleteCollectionFormModal = (treeSlug, collection) => {
    this.setState({
      showDeleteCollectionFormModel: true,
      selectedTreeSlug: treeSlug,
      selectedCollectionSlug: collection.slug,
      collectionToDelete: collection,
    });
  };

  // Close the modal
  closeDeleteCollectionFormModal = () => {
    this.setState({
      showDeleteCollectionFormModel: false,
      selectedTreeSlug: null,
      selectedCollectionSlug: null,
      collectionToDelete: null,
    });
  };

  handleDeleteCollectionFormSuccess = () => {
    this.closeDeleteCollectionFormModal();
    this.fetchData();
  };

  componentDidMount() {
    this.fetchData();
  }

  componentWillUnmount() {
    this.cancellableFetch && this.cancellableFetch.cancel();
  }

  fetchData = async () => {
    const { community } = this.props;
    this.setState({ isLoading: true });
    // Always fetch with depth 10 to get all collections
    this.cancellableFetch = withCancel(this.context.api.get_collection_trees(10));
    try {
      const response = await this.cancellableFetch.promise;
      this.setState({ data: response.data, isLoading: false });
    } catch (error) {
      const errorMessage = communityErrorSerializer(error);
      this.setState({
        error: errorMessage,
        isLoading: false,
      });
    }
  };

  renderCollectionTrees() {
    const { data, expandedTrees, draggedTreeIndex, draggedOverTreeIndex } = this.state;
    const { community } = this.props;

    // Convert to array and sort by order field to respect backend ordering
    const sortedTrees = Object.values(data).sort(
      (a, b) => (a.order || 0) - (b.order || 0)
    );

    return sortedTrees.map((collectionTree, index) => {
      const isExpanded = expandedTrees[collectionTree.id] || false;
      const collections = collectionTree.collections || [];

      const isDraggingThis = draggedTreeIndex === index;
      const isDraggedOver =
        draggedOverTreeIndex === index && draggedTreeIndex !== index;

      return (
        <div
          key={collectionTree.id}
          className={`collection-tree-section rel-mb-2 ${
            isDraggingThis ? "dragging" : ""
          } ${isDraggedOver ? "drag-over" : ""}`}
          onDragOver={(e) => this.handleTreeDragOver(e, index)}
        >
          <Grid verticalAlign="middle" className="rel-mb-1">
            <Grid.Column width={1} textAlign="center">
              <div className="category-controls">
                <Icon
                  name="bars"
                  className={`tree-drag-handle ${isDraggingThis ? "grabbing" : ""}`}
                  draggable
                  onDragStart={(e) => this.handleTreeDragStart(e, index)}
                  onDragEnd={this.handleTreeDragEnd}
                />
                <Icon
                  name={isExpanded ? "chevron down" : "chevron right"}
                  className="category-toggle"
                  onClick={() => this.toggleTreeExpansion(collectionTree.id)}
                />
              </div>
            </Grid.Column>
            <Grid.Column width={9}>
              <Header as="h2" className="category-header">
                {collectionTree.title}
              </Header>
            </Grid.Column>
            <Grid.Column width={6} textAlign="right">
              <Button
                positive
                size="small"
                onClick={() =>
                  this.openCollectionFormModal(collectionTree.id, collectionTree.slug)
                }
              >
                <Icon name="plus" /> {i18next.t("New collection")}
              </Button>
              <Button size="small" onClick={() => this.openEditModal(collectionTree)}>
                <Icon name="edit" /> {i18next.t("Edit Category")}
              </Button>
              <Button
                negative
                size="small"
                icon="trash"
                title={i18next.t("Delete Category")}
                onClick={() => this.openDeleteModal(collectionTree)}
              />
            </Grid.Column>
          </Grid>

          {isExpanded && (
            <div className="collection-tree-content">
              <CollectionTreeBrowseView
                collectionTree={collectionTree}
                collections={collections}
                onAddCollection={this.openCollectionFormModal}
                onAddChildCollection={this.openChildCollectionModal}
                onEditCollection={this.openEditCollectionFormModal}
                onDeleteCollection={this.openDeleteCollectionFormModal}
                onEditTree={this.openEditModal}
                onDeleteTree={this.openDeleteModal}
                community={community}
                showHeader={false}
                maxCollectionDepth={this.props.maxCollectionDepth}
              />
            </div>
          )}
        </div>
      );
    });
  }

  render() {
    const { isLoading, error, data, showCollectionFormModal, selectedTreeSlug } =
      this.state;
    const { emptyMessage, community } = this.props;

    return (
      <React.Fragment>
        <Grid>
          <Grid.Row>
            <Grid.Column width={12}>
              <h2>{i18next.t("Categories")}</h2>
              <p className="text-muted">
                {i18next.t(
                  "A container of collections with a visible title. Needed to group collections together."
                )}
              </p>
            </Grid.Column>
            <Grid.Column width={4} textAlign="right">
              <Button positive onClick={this.openCollectionTreeFormModal}>
                <Icon name="plus" /> {i18next.t("New category")}
              </Button>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <PlaceholderLoader isLoading={isLoading}>
                {Object.keys(data).length === 0 ? (
                  <EmptyMessage message={emptyMessage} />
                ) : (
                  this.renderCollectionTrees()
                )}
              </PlaceholderLoader>
            </Grid.Column>
          </Grid.Row>
        </Grid>
        {/* Modal for new collection form */}
        <Modal
          open={showCollectionFormModal}
          onClose={this.closeCollectionFormModal}
          size="large"
        >
          <Modal.Header>{i18next.t("Create new collection")}</Modal.Header>
          <Modal.Content>
            <NewCollectionForm
              community={community}
              collectionTreeSlug={selectedTreeSlug}
              onSuccess={this.handleCollectionFormSuccess}
              handleCancel={this.closeCollectionFormModal}
              collectionApi={this.context.api}
            />
          </Modal.Content>
        </Modal>
        <Modal
          open={this.state.showEditModal}
          onClose={this.closeEditModal}
          size="large"
        >
          <Modal.Header>{i18next.t("Edit Category")}</Modal.Header>
          <Modal.Content>
            {this.state.treeToEdit && (
              <UpdateCollectionTreeForm
                community={community}
                collectionTree={this.state.treeToEdit}
                onSuccess={this.handleEditSuccess}
                handleCancel={this.closeEditModal}
                collectionApi={this.context.api}
              />
            )}
          </Modal.Content>
        </Modal>
        {/* Modal for delete collection tree */}
        <Modal
          open={this.state.showDeleteModal}
          onClose={this.closeDeleteModal}
          size="large"
        >
          <Modal.Header>{i18next.t("Delete Category")}</Modal.Header>
          <Modal.Content>
            <DeleteCollectionTreeAction
              community={community}
              collectionTree={this.state.treeToEdit}
              hasCollections={this.state.treeToEdit?.collections?.length > 0}
              onSuccess={this.handleDeleteSuccess}
              handleCancel={this.closeDeleteModal}
              collectionApi={this.context.api}
              confirmationMessage={i18next.t(
                "Are you sure you want to delete this category? This action cannot be undone."
              )}
            />
          </Modal.Content>
        </Modal>
        {/* Modal for adding new child collection form */}
        <Modal
          open={this.state.showChildCollectionModal}
          onClose={this.closeChildCollectionModal}
          size="large"
        >
          <Modal.Header>{i18next.t("Add Child Collection")}</Modal.Header>
          <Modal.Content>
            <NewChildCollectionForm
              community={community}
              collectionTreeSlug={this.state.selectedTreeSlug}
              parentCollectionSlug={this.state.parentCollectionSlug}
              parentQuery={this.state.parentCollectionQuery}
              onSuccess={this.handleChildCollectionSuccess}
              handleCancel={this.closeChildCollectionModal}
              collectionApi={this.context.api}
            />
          </Modal.Content>
        </Modal>
        {/* Modal for editing collection form */}
        <Modal
          open={this.state.showEditCollectionFormModel}
          onClose={this.closeEditCollectionFormModal}
          size="large"
        >
          <Modal.Header>{i18next.t("Edit Collection")}</Modal.Header>
          <Modal.Content>
            <UpdateCollectionForm
              community={community}
              collectionTreeSlug={this.state.selectedTreeSlug}
              collectionSlug={this.state.selectedCollectionSlug}
              collectionData={this.state.collectionData}
              parentQuery={this.state.parentCollectionQuery}
              onSuccess={this.handleEditCollectionFormSuccess}
              handleCancel={this.closeEditCollectionFormModal}
              collectionApi={this.context.api}
            />
          </Modal.Content>
        </Modal>
        {/* Modal for editing collection form */}
        <Modal
          open={this.state.showDeleteCollectionFormModel}
          onClose={this.closeDeleteCollectionFormModal}
          size="large"
        >
          <Modal.Header>{i18next.t("Delete Collection")}</Modal.Header>
          <Modal.Content>
            <DeleteCollectionAction
              community={community}
              collectionTreeSlug={this.state.selectedTreeSlug}
              collectionSlug={this.state.selectedCollectionSlug}
              hasChildren={this.state.collectionToDelete?.children?.length > 0}
              onSuccess={this.handleDeleteCollectionFormSuccess}
              handleCancel={this.closeDeleteCollectionFormModal}
              collectionApi={this.context.api}
              confirmationMessage={i18next.t(
                "Are you sure you want to delete this collection? This action cannot be undone."
              )}
            />
          </Modal.Content>
        </Modal>
        {/* Modal for new collection tree form */}
        <Modal
          open={this.state.showCollectionTreeFormModal}
          onClose={this.closeCollectionTreeFormModal}
          size="large"
        >
          <Modal.Header>{i18next.t("Create new category")}</Modal.Header>
          <Modal.Content>
            <NewCollectionTreeForm
              community={community}
              collectionTree={{}}
              onSuccess={this.handleCollectionTreeFormSuccess}
              handleCancel={this.closeCollectionTreeFormModal}
              collectionApi={this.context.api}
            />
          </Modal.Content>
        </Modal>
      </React.Fragment>
    );
  }
}

CollectionTreeCardGroup.propTypes = {
  community: PropTypes.object.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
  emptyMessage: PropTypes.string.isRequired,
};

export default CollectionTreeCardGroup;
