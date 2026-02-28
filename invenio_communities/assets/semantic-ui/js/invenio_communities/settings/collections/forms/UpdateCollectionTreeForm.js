// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import _defaultsDeep from "lodash/defaultsDeep";
import { communityErrorSerializer } from "../../../api/serializers";
import { COLLECTION_TREE_VALIDATION_SCHEMA } from "../Configs";
import CollectionTreeForm from "./CollectionTreeForm";

class UpdateCollectionTreeForm extends Component {
  state = {
    error: "",
  };

  getInitialValues = () => {
    const { collectionTree } = this.props;
    let initialValues = _defaultsDeep(collectionTree, {
      id: "",
      title: "",
      slug: "",
    });

    return {
      ...initialValues,
    };
  };

  setGlobalError = (error) => {
    const { message } = communityErrorSerializer(error);
    this.setState({ error: message });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    values = { title: values["title"], slug: values["slug"] };
    const { collectionTree } = this.props;
    try {
      await this.props.collectionApi.update_collection_tree(
        collectionTree.slug,
        values
      );
      this.props.onSuccess();
    } catch (error) {
      if (error === "UNMOUNTED") return;
      const { message, errors } = communityErrorSerializer(error);
      if (message) {
        this.setGlobalError(error);
      }
      if (errors) {
        errors.forEach(({ field, messages }) => setFieldError(field, messages[0]));
      }
    } finally {
      setSubmitting(false);
    }
  };

  render() {
    const { slugGeneration, onFormReady } = this.props;
    const { error } = this.state;

    return (
      <CollectionTreeForm
        initialValues={this.getInitialValues()}
        validationSchema={COLLECTION_TREE_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
        handleCancel={this.props.handleCancel}
        error={error}
        slugGeneration={slugGeneration}
        onFormReady={onFormReady}
      />
    );
  }
}

UpdateCollectionTreeForm.propTypes = {
  collectionTree: PropTypes.object.isRequired,
  onSuccess: PropTypes.func.isRequired,
  handleCancel: PropTypes.func,
  slugGeneration: PropTypes.bool,
  collectionApi: PropTypes.object.isRequired,
  onFormReady: PropTypes.func,
};

UpdateCollectionTreeForm.defaultProps = {
  handleCancel: () => {},
  slugGeneration: false,
};

export default UpdateCollectionTreeForm;
