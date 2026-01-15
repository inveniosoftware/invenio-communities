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
import { Button, Card, Grid, Icon, Modal } from "semantic-ui-react";
import { communityErrorSerializer } from "../../api/serializers";
import { CollectionsContext } from "../../api/collections/CollectionsContextProvider";
import CollectionsTable from "./components/CollectionsTable";
import CollectionTreeCard from "./components/CollectionTreeCard";
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
      selectedTreeId: null,
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
      collectionToDelete: null,
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
    this.setState({
      showChildCollectionModal: true,
      selectedTreeSlug: treeSlug,
      parentCollectionSlug: parentSlug,
    });
  };

  // Close the modal
  closeChildCollectionModal = () => {
    this.setState({
      showChildCollectionModal: false,
      parentCollectionSlug: null,
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

  // Handle selection of collection for tree
  handleTreeSelection = (treeId) => {
    this.setState(
      (prevState) => ({
        selectedTreeId: prevState.selectedTreeId === treeId ? null : treeId,
      }),
      () => {
        // Refetch data with appropriate depth after state is updated
        this.fetchData();
      }
    );
  };

  openCollectionFormModal = (treeId, treeSlug) => {
    this.setState({
      showCollectionFormModal: true,
      selectedTreeId: treeId,
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
    this.setState({
      showEditCollectionFormModel: true,
      selectedTreeSlug: treeSlug,
      selectedCollectionSlug: collection.slug,
      collectionData: collection,
    });
  };

  // Close the modal
  closeEditCollectionFormModal = () => {
    this.setState({
      showEditCollectionFormModel: false,
      selectedCollectionSlug: null,
      selectedTreeSlug: null,
      collectionData: null,
    });
  };

  handleEditCollectionFormSuccess = () => {
    this.closeEditCollectionFormModal();
    this.fetchData();
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
    const { selectedTreeId } = this.state;
    this.setState({ isLoading: true });
    const depth = selectedTreeId ? 10 : 1;
    this.cancellableFetch = withCancel(this.context.api.get_collection_trees(depth));
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

  renderCards() {
    const { data } = this.state;

    return Object.entries(data).map(([key, collectionTree]) => {
      return (
        <CollectionTreeCard
          key={collectionTree.id}
          collectionTree={collectionTree}
          onViewClick={this.handleTreeSelection}
          onEditClick={this.openEditModal}
          onDeleteClick={this.openDeleteModal}
          isSelected={this.state.selectedTreeId === collectionTree.id}
        />
      );
    });
  }

  render() {
    const {
      isLoading,
      error,
      data,
      selectedTreeId,
      showCollectionFormModal,
      selectedTreeSlug,
    } = this.state;
    const { emptyMessage, community } = this.props;

    // Find the selected tree if any
    let selectedTree = null;
    let collections = [];

    if (selectedTreeId && data) {
      selectedTree = Object.values(data).find((tree) => tree.id === selectedTreeId);
      collections = selectedTree ? selectedTree.collections || [] : [];
    }

    return (
      <React.Fragment>
        <Grid>
          <Grid.Row>
            <Grid.Column width={12}>
              <h2>{i18next.t("Collection Trees")}</h2>
            </Grid.Column>
            <Grid.Column width={4} textAlign="right">
              <Button positive onClick={this.openCollectionTreeFormModal}>
                <Icon name="plus" /> {i18next.t("New collection tree")}
              </Button>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <PlaceholderLoader isLoading={isLoading}>
                {Object.keys(data).length === 0 ? (
                  <EmptyMessage message={emptyMessage} />
                ) : (
                  <Card.Group
                    doubling
                    stackable
                    itemsPerRow={5}
                    className="faculty-profile-frontpage-cards"
                  >
                    {this.renderCards()}
                  </Card.Group>
                )}
              </PlaceholderLoader>
            </Grid.Column>
          </Grid.Row>
          {selectedTree && (
            <Grid.Row>
              <Grid.Column>
                <CollectionsTable
                  collections={collections}
                  collectionTreeTitle={selectedTree.title}
                  onAddCollection={this.openCollectionFormModal}
                  onAddChildCollection={this.openChildCollectionModal}
                  onEditCollection={this.openEditCollectionFormModal}
                  onDeleteCollection={this.openDeleteCollectionFormModal}
                  collectionTreeId={selectedTree.id}
                  collectionTreeSlug={selectedTree.slug}
                />
              </Grid.Column>
            </Grid.Row>
          )}
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
          <Modal.Header>{i18next.t("Edit Collection Tree")}</Modal.Header>
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
          <Modal.Header>{i18next.t("Delete Collection Tree")}</Modal.Header>
          <Modal.Content>
            <DeleteCollectionTreeAction
              community={community}
              collectionTree={this.state.treeToEdit}
              hasCollections={this.state.treeToEdit?.collections?.length > 0}
              onSuccess={this.handleDeleteSuccess}
              handleCancel={this.closeDeleteModal}
              collectionApi={this.context.api}
              confirmationMessage={i18next.t(
                "Are you sure you want to delete this collection tree? This action cannot be undone."
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
          <Modal.Header>{i18next.t("Create new collection tree")}</Modal.Header>
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
  emptyMessage: PropTypes.string.isRequired,
};

export default CollectionTreeCardGroup;
