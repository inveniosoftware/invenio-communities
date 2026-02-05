// This file is part of Invenio-Communities
// Copyright (C) 2026 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useEffect, memo } from "react";
import PropTypes from "prop-types";
import { Grid, Header, Label, Dropdown, Icon, Container } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";

/**
 * Helper function to generate action menu options for a collection.
 * @param {Object} collection - The collection object
 * @param {number} maxCollectionDepth - Maximum allowed collection depth
 * @param {Function} onEdit - Edit callback
 * @param {Function} onDelete - Delete callback
 * @param {Function} onAddChild - Add child callback
 * @returns {Array} Array of action menu option objects
 */
const getActionMenuOptions = (
  collection,
  maxCollectionDepth,
  onEdit,
  onDelete,
  onAddChild
) => [
  {
    key: "edit",
    text: i18next.t("Edit"),
    icon: "edit",
    onClick: () => onEdit(collection),
  },
  ...(collection.depth < maxCollectionDepth
    ? [
        {
          key: "add-child",
          text: i18next.t("Add Child"),
          icon: "plus",
          onClick: () => onAddChild(collection),
        },
      ]
    : []),
  {
    key: "delete",
    text: i18next.t("Delete"),
    icon: "trash",
    onClick: () => onDelete(collection),
  },
];

const CollectionBrowseCard = ({
  collection,
  allCollections,
  onEdit,
  onDelete,
  onAddChild,
  community,
  collectionApi,
  treeSlug,
  isDraggable = false,
  dragIndex = null,
  onDragStart = null,
  onDragEnd = null,
  isDragging = false,
  maxCollectionDepth,
}) => {
  const [childrenOrder, setChildrenOrder] = useState([]);
  const [draggedChildIndex, setDraggedChildIndex] = useState(null);
  const [draggedOverChildIndex, setDraggedOverChildIndex] = useState(null);

  useEffect(() => {
    setChildrenOrder(collection.children || []);
  }, [collection.children]);

  /**
   * Handle the start of dragging a child collection.
   * @param {DragEvent} e - The drag event
   * @param {number} index - Index of the child being dragged
   */
  const handleChildDragStart = (e, index) => {
    setDraggedChildIndex(index);
    e.dataTransfer.effectAllowed = "move";
  };

  /**
   * Handle dragging over a child collection position.
   * @param {DragEvent} e - The drag event
   * @param {number} index - Index of the position being dragged over
   */
  const handleChildDragOver = (e, index) => {
    if (draggedChildIndex === null) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = "move";

    if (index !== draggedOverChildIndex) {
      setDraggedOverChildIndex(index);
    }
  };

  /**
   * Handle the end of dragging a child collection.
   * Performs optimistic UI update and persists order to backend.
   * Reverts on error.
   * @param {DragEvent} e - The drag event
   */
  const handleChildDragEnd = async (e) => {
    e.stopPropagation();

    if (
      draggedChildIndex === null ||
      draggedOverChildIndex === null ||
      draggedChildIndex === draggedOverChildIndex
    ) {
      setDraggedChildIndex(null);
      setDraggedOverChildIndex(null);
      return;
    }

    // Reorder array
    const items = Array.from(childrenOrder);
    const [reorderedItem] = items.splice(draggedChildIndex, 1);
    items.splice(draggedOverChildIndex, 0, reorderedItem);

    // Optimistic UI update
    setChildrenOrder(items);
    setDraggedChildIndex(null);
    setDraggedOverChildIndex(null);

    // Persist to backend
    if (collectionApi && treeSlug) {
      try {
        const orderPayload = {
          order: items
            .map((childId, index) => {
              const child = allCollections[childId];
              if (!child) {
                console.warn(`Child collection with id ${childId} not found`);
                return null;
              }
              return {
                slug: child.slug,
                order: (index + 1) * 10,
              };
            })
            .filter(Boolean),
        };

        await collectionApi.batch_reorder_collections(treeSlug, orderPayload);
      } catch (error) {
        console.error("Failed to update child collection order:", error);
        // Revert on error
        setChildrenOrder(collection.children || []);
      }
    }
  };

  const actionMenuOptions = getActionMenuOptions(
    collection,
    maxCollectionDepth,
    onEdit,
    onDelete,
    onAddChild
  );

  const parentCollectionUrl = community
    ? `/communities/${community.slug}/collections/${treeSlug}/${collection.slug}`
    : null;

  return (
    <Container className="mt-0 mb-0 rel-ml-1 collection-browse-card">
      {/* Logo + Title + Record Count */}
      <div className="content rel-mb-1">
        <Grid>
          <Grid.Column width={10} className="middle aligned">
            <div className="flex align-items-center">
              {isDraggable && onDragStart && (
                <Icon
                  name="bars"
                  className={`parent-drag-handle ${isDragging ? "grabbing" : ""}`}
                  draggable
                  onDragStart={(e) => onDragStart(e, dragIndex)}
                  onDragEnd={onDragEnd}
                  tabIndex={0}
                  role="button"
                />
              )}
              {parentCollectionUrl ? (
                <a
                  href={parentCollectionUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="collection-link"
                >
                  <Header as="h4" className="collection-title mt-0">
                    {collection.title}
                  </Header>
                </a>
              ) : (
                <Header as="h4" className="collection-title theme-primary-text mt-0">
                  {collection.title}
                </Header>
              )}
            </div>
          </Grid.Column>
          <Grid.Column width={3} className="middle aligned collection-number">
            <Label size="small">{collection.num_records || 0}</Label>
          </Grid.Column>
          <Grid.Column width={3} className="middle aligned" textAlign="right">
            <Dropdown
              icon="ellipsis vertical"
              floating
              button
              className="icon collection-actions-menu"
            >
              <Dropdown.Menu direction="left">
                {actionMenuOptions.map((option) => (
                  <Dropdown.Item
                    key={option.key}
                    icon={option.icon}
                    text={option.text}
                    onClick={option.onClick}
                  />
                ))}
              </Dropdown.Menu>
            </Dropdown>
          </Grid.Column>
        </Grid>
      </div>

      {childrenOrder.length > 0 && (
        <div className="content">
          {childrenOrder.map((childSlug, index) => {
            const child = allCollections[childSlug];
            if (!child) return null;

            const {
              title,
              num_records: numRecords,
              depth,
              children: childChildren,
            } = child;

            const childActionMenuOptions = getActionMenuOptions(
              child,
              maxCollectionDepth,
              onEdit,
              onDelete,
              onAddChild
            );

            const collectionUrl = community
              ? `/communities/${community.slug}/collections/${treeSlug}/${child.slug}`
              : null;

            const isChildDragging = draggedChildIndex === index;
            const isChildDraggedOver =
              draggedOverChildIndex === index && draggedChildIndex !== index;

            return (
              <div key={childSlug}>
                <Container
                  className={`mb-0 mt-0 collection-child-item ${
                    isChildDragging ? "dragging" : ""
                  } ${isChildDraggedOver ? "drag-over" : ""}`}
                  onDragOver={(e) => handleChildDragOver(e, index)}
                >
                  <div className="child-collection-row">
                    <Icon
                      name="bars"
                      className={`child-drag-handle ${
                        isChildDragging ? "grabbing" : ""
                      }`}
                      draggable
                      onDragStart={(e) => handleChildDragStart(e, index)}
                      onDragEnd={handleChildDragEnd}
                      tabIndex={0}
                      role="button"
                    />
                    <div className="child-collection-content">
                      {collectionUrl ? (
                        <a
                          href={collectionUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="collection-link truncated"
                          title={title}
                        >
                          <Header as="h5" className="truncated">
                            {title}
                          </Header>
                        </a>
                      ) : (
                        <Header
                          as="h5"
                          className="theme-primary-text truncated"
                          title={title}
                        >
                          {title}
                        </Header>
                      )}
                      <Label
                        size="tiny"
                        className="child-collection-label text-muted ml-1"
                      >
                        ({numRecords || 0})
                      </Label>
                    </div>
                    <Dropdown
                      icon="ellipsis vertical"
                      floating
                      button
                      className="child-collection-actions icon mini collection-actions-menu"
                    >
                      <Dropdown.Menu direction="left">
                        {childActionMenuOptions.map((option) => (
                          <Dropdown.Item
                            key={option.key}
                            icon={option.icon}
                            text={option.text}
                            onClick={option.onClick}
                          />
                        ))}
                      </Dropdown.Menu>
                    </Dropdown>
                  </div>
                </Container>
                {/* Recursively render grandchildren and deeper levels */}
                {childChildren && childChildren.length > 0 && (
                  <div className="nested-children">
                    {childChildren.map((grandchildSlug) => {
                      const grandchild = allCollections[grandchildSlug];
                      if (!grandchild) return null;

                      return (
                        <NestedCollectionItem
                          key={grandchildSlug}
                          collection={grandchild}
                          allCollections={allCollections}
                          onEdit={onEdit}
                          onDelete={onDelete}
                          onAddChild={onAddChild}
                          maxCollectionDepth={maxCollectionDepth}
                          nestingLevel={1}
                          community={community}
                          treeSlug={treeSlug}
                        />
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Container>
  );
};

CollectionBrowseCard.propTypes = {
  collection: PropTypes.shape({
    id: PropTypes.string,
    slug: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    num_records: PropTypes.number,
    children: PropTypes.array,
    depth: PropTypes.number,
  }).isRequired,
  allCollections: PropTypes.object.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  onAddChild: PropTypes.func.isRequired,
  community: PropTypes.object,
  collectionApi: PropTypes.object,
  treeSlug: PropTypes.string,
  isDraggable: PropTypes.bool,
  dragIndex: PropTypes.number,
  onDragStart: PropTypes.func,
  onDragEnd: PropTypes.func,
  isDragging: PropTypes.bool,
  maxCollectionDepth: PropTypes.number.isRequired,
};

CollectionBrowseCard.defaultProps = {
  community: null,
  collectionApi: null,
  treeSlug: null,
  isDraggable: false,
  dragIndex: null,
  onDragStart: null,
  onDragEnd: null,
  isDragging: false,
};

/**
 * Recursive component for rendering nested child collections.
 * Displays collection information with edit/delete/add actions and
 * recursively renders all descendant collections with visual indentation.
 *
 * Wrapped with React.memo for performance optimization.
 *
 * @component
 * @param {Object} props - Component props
 * @param {Object} props.collection - The collection to render
 * @param {Object} props.allCollections - Map of all collections by slug
 * @param {Function} props.onEdit - Callback when edit is clicked
 * @param {Function} props.onDelete - Callback when delete is clicked
 * @param {Function} props.onAddChild - Callback when add child is clicked
 * @param {number} props.maxCollectionDepth - Maximum allowed collection depth
 * @param {number} [props.nestingLevel=1] - Current nesting level for indentation
 * @param {Object} props.community - Community object
 * @param {string} props.treeSlug - Collection tree slug
 */
const NestedCollectionItem = memo(
  ({
    collection,
    allCollections,
    onEdit,
    onDelete,
    onAddChild,
    maxCollectionDepth,
    nestingLevel = 1,
    community,
    treeSlug,
  }) => {
    const { title, num_records: numRecords, depth, children, slug } = collection;

    const [childrenOrder, setChildrenOrder] = useState([]);

    useEffect(() => {
      setChildrenOrder(children || []);
    }, [children]);

    const actionMenuOptions = getActionMenuOptions(
      collection,
      maxCollectionDepth,
      onEdit,
      onDelete,
      onAddChild
    );

    const collectionUrl = community
      ? `/communities/${community.slug}/collections/${treeSlug}/${slug}`
      : null;

    return (
      <div className="nested-collection-item" data-nesting-level={nestingLevel}>
        <Container className="mb-0 mt-0 collection-child-item">
          <div className="child-collection-row">
            <div className="child-collection-content">
              {collectionUrl ? (
                <a
                  href={collectionUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="collection-link truncated"
                  title={title}
                >
                  <Header as="h5" className="truncated">
                    {title}
                  </Header>
                </a>
              ) : (
                <Header as="h5" className="theme-primary-text truncated" title={title}>
                  {title}
                </Header>
              )}
              <Label size="tiny" className="child-collection-label text-muted ml-1">
                ({numRecords || 0})
              </Label>
            </div>
            <Dropdown
              icon="ellipsis vertical"
              floating
              button
              className="child-collection-actions icon mini collection-actions-menu"
            >
              <Dropdown.Menu direction="left">
                {actionMenuOptions.map((option) => (
                  <Dropdown.Item
                    key={option.key}
                    icon={option.icon}
                    text={option.text}
                    onClick={option.onClick}
                  />
                ))}
              </Dropdown.Menu>
            </Dropdown>
          </div>
        </Container>

        {/* RECURSION: Render this collection's children */}
        {childrenOrder.length > 0 && (
          <div className="nested-children">
            {childrenOrder.map((childSlug) => {
              const child = allCollections[childSlug];
              if (!child) return null;

              return (
                <NestedCollectionItem
                  key={childSlug}
                  collection={child}
                  allCollections={allCollections}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onAddChild={onAddChild}
                  maxCollectionDepth={maxCollectionDepth}
                  nestingLevel={nestingLevel + 1}
                  community={community}
                  treeSlug={treeSlug}
                />
              );
            })}
          </div>
        )}
      </div>
    );
  }
);

NestedCollectionItem.displayName = "NestedCollectionItem";

NestedCollectionItem.propTypes = {
  collection: PropTypes.object.isRequired,
  allCollections: PropTypes.object.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  onAddChild: PropTypes.func.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
  nestingLevel: PropTypes.number,
  community: PropTypes.object,
  treeSlug: PropTypes.string,
};

export default CollectionBrowseCard;
