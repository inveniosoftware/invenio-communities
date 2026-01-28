// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { communityErrorSerializer } from "../../../api/serializers";
import { COLLECTION_VALIDATION_SCHEMA } from "../Configs";
import CollectionForm from "./CollectionForm";

class NewChildCollectionForm extends Component {
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
      order: 1,
    };
  };

  setGlobalError = (error) => {
    const { message } = communityErrorSerializer(error);
    this.setState({ error: message });
  };

  onTest = async (values) => {
    const { collectionTreeSlug, parentCollectionSlug } = this.props;

    try {
      const response = await this.props.collectionApi.test_search_query_for_collection(
        collectionTreeSlug,
        parentCollectionSlug,
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
        testQueryResult: error.response.data.message,
      });
    }
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    const { collectionTreeSlug, parentCollectionSlug, onSuccess } = this.props;

    try {
      await this.props.collectionApi.add_collection(
        collectionTreeSlug,
        parentCollectionSlug,
        values
      );
      onSuccess();
    } catch (error) {
      if (error === "UNMOUNTED") return;
      const { message, errors } = communityErrorSerializer(error);
      setSubmitting(false);
      if (message) {
        this.setGlobalError(error);
      }
      if (errors) {
        errors.map(({ field, messages }) => setFieldError(field, messages[0]));
      }
    } finally {
      setSubmitting(false);
    }
  };

  render() {
    const { slugGeneration, community, parentQuery } = this.props;
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
        parentQuery={parentQuery}
      />
    );
  }
}

NewChildCollectionForm.propTypes = {
  collectionTreeSlug: PropTypes.string.isRequired,
  parentCollectionSlug: PropTypes.string.isRequired,
  onSuccess: PropTypes.func.isRequired,
  handleCancel: PropTypes.func,
  slugGeneration: PropTypes.bool,
  collectionApi: PropTypes.object.isRequired,
  community: PropTypes.object,
  parentQuery: PropTypes.string,
};

NewChildCollectionForm.defaultProps = {
  handleCancel: () => {},
  slugGeneration: true,
};

export default NewChildCollectionForm;
