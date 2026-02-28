// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Formik } from "formik";
import { Button, Form, Grid, Message, Divider } from "semantic-ui-react";
import { FieldLabel, TextField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_communities/i18next";
import { generateSlug } from "../Configs";

const CollectionForm = ({
  initialValues,
  validationSchema,
  onSubmit,
  onTest,
  handleCancel,
  testQueryResult,
  testQuerySuccess,
  testQueryHits,
  error,
  slugGeneration,
  community,
  parentQuery,
  onFormReady,
}) => {
  // Build the full search query including parent query if it exists
  const buildFullSearchQuery = (currentQuery) => {
    if (parentQuery && currentQuery) {
      return `(${parentQuery}) AND (${currentQuery})`;
    }
    return currentQuery || parentQuery || "";
  };
  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onSubmit}
      validateOnChange={false}
      validateOnBlur={false}
    >
      {({ isSubmitting, isValid, handleSubmit, ...formik }) => {
        // Call onFormReady to expose formik state to parent
        if (onFormReady) {
          onFormReady({ isSubmitting, isValid, handleSubmit, handleCancel });
        }
        return (
          <Form onSubmit={handleSubmit} className="communities-collection">
            <Message hidden={error === ""} negative>
              <Grid container>
                <Grid.Column width={15} textAlign="left">
                  <strong>{error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid>
              <Grid.Row>
                <Grid.Column as="section" mobile={16} tablet={16} computer={16}>
                  <TextField
                    required
                    fluid
                    fieldPath="title"
                    label={
                      <FieldLabel
                        htmlFor="title"
                        icon="header"
                        label={i18next.t("Title")}
                      />
                    }
                    onChange={
                      slugGeneration
                        ? (event, { value }) => {
                            formik.setFieldValue("title", value);
                            formik.setFieldValue("slug", generateSlug(value));
                          }
                        : (event, { value }) => {
                            formik.setFieldValue("title", value);
                          }
                    }
                  />
                  <TextField
                    required
                    fluid
                    fieldPath="slug"
                    label={
                      <FieldLabel
                        htmlFor="slug"
                        icon="linkify"
                        label={i18next.t("Slug")}
                      />
                    }
                  />

                  {/* Search Query with Test Button */}
                  <Form.Field required>
                    <FieldLabel
                      htmlFor="search_query"
                      icon="search"
                      label={i18next.t("Search Query")}
                    />
                    <Form.Group>
                      <Form.Input
                        id="search_query"
                        name="search_query"
                        value={formik.values.search_query}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        error={
                          formik.touched.search_query && formik.errors.search_query
                        }
                        width={13}
                      />
                      <Form.Field width={3}>
                        <Button
                          type="button"
                          fluid
                          onClick={(e) => {
                            e.preventDefault();
                            onTest(formik.values);
                          }}
                        >
                          {i18next.t("Test Query")}
                        </Button>
                      </Form.Field>
                    </Form.Group>
                  </Form.Field>
                </Grid.Column>
              </Grid.Row>
            </Grid>

            {/* Test Query Results */}
            {testQueryResult !== null && (
              <Message
                hidden={testQueryResult === null}
                positive={testQuerySuccess === true && testQueryResult > 0}
                neutral={testQuerySuccess === true && testQueryResult === 0}
                negative={testQuerySuccess === false}
                className="rel-mb-2"
              >
                {testQuerySuccess === true
                  ? i18next.t("Total Hits: ") + testQueryResult
                  : testQueryResult}
                {testQuerySuccess === true && testQueryHits.length > 0 && (
                  <div className="rel-mt-1">
                    <em>
                      {i18next.t("Showing")} {testQueryHits.length}{" "}
                      {i18next.t("example results:")}
                    </em>
                  </div>
                )}
                {testQuerySuccess === true && (
                  <Message.List>
                    {testQueryHits.map((hit, index) => (
                      <Message.Item key={index}>
                        {hit["metadata"]["title"]}
                      </Message.Item>
                    ))}
                  </Message.List>
                )}
                {testQuerySuccess === true && testQueryResult > 0 && community && (
                  <div className="rel-mt-1">
                    <Button
                      as="a"
                      href={`/communities/${
                        community.slug
                      }/records?q=${encodeURIComponent(
                        buildFullSearchQuery(formik.values.search_query)
                      )}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      icon="external"
                      content={i18next.t("View Full Results")}
                      size="small"
                    />
                  </div>
                )}
              </Message>
            )}
          </Form>
        );
      }}
    </Formik>
  );
};

CollectionForm.propTypes = {
  initialValues: PropTypes.object.isRequired,
  validationSchema: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onTest: PropTypes.func.isRequired,
  handleCancel: PropTypes.func.isRequired,
  testQueryResult: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  testQuerySuccess: PropTypes.bool,
  testQueryHits: PropTypes.array,
  error: PropTypes.string,
  slugGeneration: PropTypes.bool,
  community: PropTypes.object,
  parentQuery: PropTypes.string,
  onFormReady: PropTypes.func,
};

CollectionForm.defaultProps = {
  testQueryResult: null,
  testQuerySuccess: null,
  testQueryHits: [],
  error: "",
  slugGeneration: false,
  community: null,
  parentQuery: null,
};

export default CollectionForm;
