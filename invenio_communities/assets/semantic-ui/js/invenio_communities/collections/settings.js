/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { useState } from "react";
import ReactDOM from "react-dom";
import { TextField } from "react-invenio-forms";
import { Formik } from "formik";

import { Form, Button, Icon, Item } from "semantic-ui-react";
import axios from "axios";
import * as Yup from "yup";
import { RichInputField } from "../forms";

const CollectionForm = ({ collection, onSubmit }) => {
  return (
    <Formik
      onSubmit={onSubmit}
      initialValues={{
        // id: collection.id || "",
        title: collection.title || "",
        description: collection.description || "",
      }}
      validationSchema={Yup.object({
        // id: Yup.string()
        //   .required("Required")
        //   .max(32, "Must be 32 characters or less"),
        title: Yup.string()
          .max(120, "Must be 120 characters or less")
          .required("Required"),
        description: Yup.string().max(250, "Must be 250 characters or less"),
      })}
    >
      {({ isSubmitting, handleSubmit }) => (
        <Form onSubmit={handleSubmit}>
          {/* <TextField fieldPath="id" label="ID" required /> */}
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

const CollectionItem = ({ collection_id, collection }) => {
  const [editing, setEditing] = useState(false);
  // const [collection, setCollection] = useState(collection);

  const onEditSubmit = (data) => {
    console.log(data);
    axios
      .put(
        `/api/communities/${__COMMUNITY.id}/collections/${collection_id}`,
        data
      )
      .then((resp) => {
        setEditing(false);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <Item>
      {!editing ? (
        <Item.Content>
          <Item.Header>{collection.title}</Item.Header>
          <Item.Meta>{collection_id}</Item.Meta>
          <Item.Description>{collection.description}</Item.Description>
          <Item.Extra>
            <Button primary size="mini" onClick={() => setEditing(true)}>
              <Icon name="edit" /> Edit
            </Button>
          </Item.Extra>
        </Item.Content>
      ) : (
        <CollectionForm collection={collection} onSubmit={onEditSubmit} />
      )}
    </Item>
  );
};

const CollectionsList = ({ collections }) => {
  return (
    <>
      <Item.Group>
        {__COLLECTIONS &&
          Object.entries(__COLLECTIONS).map(([collection_id, collection]) => {
            return (
              <CollectionItem
                key={collection_id}
                collection_id={collection_id}
                collection={collection}
              />
            );
          })}
      </Item.Group>
      <Button size="small" positive>
        <Icon name="plus" /> New collection
      </Button>
    </>
  );
};

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const __COLLECTIONS = formConfig.collections;
const __COMMUNITY = formConfig.community;
ReactDOM.render(<CollectionsList />, domContainer);
