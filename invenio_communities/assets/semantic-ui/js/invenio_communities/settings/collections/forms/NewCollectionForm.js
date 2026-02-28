// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { communityErrorSerializer } from "../../../api/serializers";
import _cloneDeep from "lodash/cloneDeep";
import { removeEmptyValues } from "../utils";
import { COLLECTION_VALIDATION_SCHEMA } from "../Configs";
import CollectionForm from "./CollectionForm";

class NewCollectionForm extends Component {
  state = {
    error: "",
    testQueryResult: null,
    testQuerySuccess: null,
    testQueryHits: [],
  };

  getInitialValues = () => {
    return {
      title: "",
      slug: "",
      search_query: "*",
    };
  };

  serializeValues = (values) => {
    let submittedCollection = _cloneDeep(values);
    submittedCollection = removeEmptyValues(submittedCollection);
    return submittedCollection;
  };

  setGlobalError = (error) => {
    const { message } = communityErrorSerializer(error);
    this.setState({ error: message });
  };

  onTest = async (values) => {
    const { collectionTreeSlug } = this.props;

    try {
      const response =
        await this.props.collectionApi.test_search_query_for_base_collection(
          collectionTreeSlug,
          values
        );
      this.setState({
        testQuerySuccess: true,
        testQueryResult: response.data.hits.total,
        testQueryHits: response.data.hits.hits,
      });
    } catch (error) {
      this.setState({
        testQuerySuccess: false,
        testQueryResult: error.response?.data?.message || "Network error",
      });
    }
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    let payload = this.serializeValues(values);
    const { collectionTreeSlug } = this.props;

    try {
      await this.props.collectionApi.create_collection(collectionTreeSlug, payload);
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
    const { slugGeneration, community, onFormReady } = this.props;
    const { testQueryResult, testQuerySuccess, testQueryHits, error } = this.state;

    return (
      <CollectionForm
        initialValues={this.getInitialValues()}
        validationSchema={COLLECTION_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
        onTest={this.onTest}
        handleCancel={this.props.handleCancel}
        testQueryResult={testQueryResult}
        testQuerySuccess={testQuerySuccess}
        testQueryHits={testQueryHits}
        error={error}
        slugGeneration={slugGeneration}
        community={community}
        onFormReady={onFormReady}
      />
    );
  }
}

NewCollectionForm.propTypes = {
  collectionTreeSlug: PropTypes.string.isRequired,
  onSuccess: PropTypes.func,
  handleCancel: PropTypes.func,
  slugGeneration: PropTypes.bool,
  collectionApi: PropTypes.object.isRequired,
  community: PropTypes.object,
  onFormReady: PropTypes.func,
};

NewCollectionForm.defaultProps = {
  onSuccess: () => {},
  handleCancel: () => {},
  slugGeneration: true,
};

export default NewCollectionForm;
