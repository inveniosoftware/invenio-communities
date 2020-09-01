/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { useState } from "react";
import ReactDOM from "react-dom";
import _isEmpty from 'lodash/isEmpty';
import { TextField } from "react-invenio-forms";
import { Formik } from "formik";

import { Form, Button, Icon, Item, Confirm } from "semantic-ui-react";
import axios from "axios";
import * as Yup from "yup";
import { RichInputField } from "../forms";

const CollectionForm = ({ collection = {}, collection_id = '', isNewCollection, onSubmit }) => {
  return (
    <Formik
      onSubmit={onSubmit}
      initialValues={{
        id: collection.id || collection_id,
        title: collection.title || "",
        description: collection.description || "",
      }}
      validationSchema={Yup.object({
        id: Yup.string()
          .required("Required")
          .max(32, "Must be 32 characters or less"),
        title: Yup.string()
          .max(120, "Must be 120 characters or less")
          .required("Required"),
        description: Yup.string().max(250, "Must be 250 characters or less"),
      })}
    >
      {({ isSubmitting, handleSubmit }) => (
        <Form onSubmit={handleSubmit}>
          {isNewCollection ? <TextField fieldPath="id" label="ID" required /> : null}
          <TextField fieldPath="title" label="Title" required />
          <RichInputField fieldPath="description" label="Description" />
          <button disabled={isSubmitting} className="ui positive button small" type="submit">
            Submit
          </button>
        </Form>
      )}
    </Formik>
  );
};

const CollectionItem = ({ collection_id, collection, setCollections, collections }) => {
  const [editing, setEditing] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  // const [collection, setCollection] = useState(collection);
  let isNewCollection = collection.isNewCollection

  const onEditSubmit = (data) => {
    axios
      .put(
        `/api/communities/${__COMMUNITY.id}/collections/${collection_id}`,
        data
      )
      .then((resp) => {
        let {[collection_id]: edited_collection, ...new_collections} = collections
        let updated_collection = {
          [data.id]: {
            'title': data.title,
            'description': data.description
          }
        }
        setCollections({...updated_collection, ...new_collections})
        setEditing(false);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const removeCollection = (collection_id) => {
    axios
      .delete(
        `/api/communities/${__COMMUNITY.id}/collections/${collection_id}`
      )
      .then((resp) => {
        let {[collection_id]: removed_collection, ...new_collections} = collections
        setCollections(new_collections)
        setShowConfirm(false);
      })
      .catch((error) => {
        console.log(error);
      });
  };
  if (!editing && isNewCollection) {
    setEditing(true)
  }

  let confirmContent = `Are you sure you want to delete the collection: ${collection.title}`

  return (
    <Item>
      {!editing ? (
        <Item.Content>
          <Item.Header>{collection.title}</Item.Header>
          <Item.Meta>{collection_id}</Item.Meta>
          <Item.Description>
            <div
              dangerouslySetInnerHTML={{ __html: collection.description }}
            />
          </Item.Description>
          <Item.Extra>
            <Button primary size="mini" onClick={() => setEditing(true)}>
              <Icon name="edit" /> Edit
            </Button>
            <Button primary negative size="mini" onClick={() => setShowConfirm(true)}>
              <Icon name="delete" /> Delete
            </Button>
            <Confirm
              open={showConfirm}
              content={confirmContent}
              onCancel={() => setShowConfirm(false)}
              onConfirm={() => removeCollection(collection_id)}
            />
          </Item.Extra>
        </Item.Content>
      ) : (
          <CollectionForm
            collection={collection}
            collection_id={collection_id}
            onSubmit={onEditSubmit}
            isNewCollection={false}
          />
        )}
    </Item>
  );
};

const CollectionsList = () => {
  const [collections, setCollections] = useState(__COLLECTIONS);
  const [collectionAddition, setcollectionAddition] = useState(false);

  const addNewCollection = (collection) => {
    setCollections({ ...collection, ...collections });
  }

  const removeNewCollection = () => {
    setcollectionAddition(false);
  }
  if (!collectionAddition && _isEmpty(collections)) {
    setcollectionAddition(true);
  }

  const onCreateSubmit = (data) => {
    console.log(data)
    axios
      .post(
        `/api/communities/${__COMMUNITY.id}/collections`,
        data
      )
      .then((resp) => {
        addNewCollection(
          {
            [data.id]: {
              'title': data.title,
              'description': data.description
            }
          }
        )
        setcollectionAddition(false);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <div className="ui divided items" >
      {collections &&
        Object.entries(collections).sort().map(([collection_id, collection]) => {
          return (
            <CollectionItem
              key={collection_id}
              collection_id={collection_id}
              collection={collection}
              setCollections={setCollections}
              collections={collections}
            />
          );
        })}
      {collectionAddition ?
        <>
          <CollectionForm
            onSubmit={onCreateSubmit}
            isNewCollection={true}
          />
          <Button className="ui right floated negative button small" onClick={() => removeNewCollection()}>
            Remove
              </Button>
        </>
        : null}
      <Button size="small" positive disabled={collectionAddition} onClick={() => setcollectionAddition(true)}>
        <Icon name="plus" /> New collection
      </Button>
    </div>

  );
};



const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const __COLLECTIONS = formConfig.collections;
const __COMMUNITY = formConfig.community;
ReactDOM.render(<CollectionsList />, domContainer);
