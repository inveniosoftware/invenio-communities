// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Formik } from "formik";
import { Button, Form, Grid, Icon, Message, Divider } from "semantic-ui-react";
import { AccordionField, FieldLabel, TextField } from "react-invenio-forms";
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
}) => {
  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onSubmit}
    >
      {({ isSubmitting, isValid, handleSubmit, ...formik }) => (
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
              <Grid.Column
                as="section"
                mobile={16}
                tablet={16}
                computer={16}
                className="rel-pb-2"
              >
                <AccordionField
                  includesPaths={["title", "slug", "search_query", "order"]}
                  label={i18next.t("Collection information")}
                  active
                >
                  <div className="rel-ml-1 rel-mr-1">
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
                    <TextField
                      required
                      fluid
                      fieldPath="search_query"
                      label={
                        <FieldLabel
                          htmlFor="search_query"
                          icon="search"
                          label={i18next.t("Search Query")}
                        />
                      }
                    />
                    <TextField
                      fluid
                      fieldPath="order"
                      type="number"
                      label={
                        <FieldLabel
                          htmlFor="order"
                          icon="sort"
                          label={i18next.t("Order")}
                        />
                      }
                    />
                  </div>
                </AccordionField>
                <Divider hidden />
                <Button
                  disabled={!isValid || isSubmitting}
                  loading={isSubmitting}
                  labelPosition="left"
                  primary
                  type="submit"
                  icon
                >
                  <Icon name="save" />
                  {i18next.t("Save")}
                </Button>
                <Button
                  primary
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    onTest(formik.values);
                  }}
                >
                  {i18next.t("Test Query")}
                </Button>
                <Button
                  labelPosition="left"
                  secondary
                  type="button"
                  icon
                  onClick={handleCancel}
                >
                  <Icon name="cancel" />
                  {i18next.t("Cancel")}
                </Button>
              </Grid.Column>
            </Grid.Row>
          </Grid>
          {testQueryResult !== null && (
            <Message
              hidden={testQueryResult === null}
              positive={testQuerySuccess === true && testQueryResult > 0}
              neutral={testQuerySuccess === true && testQueryResult === 0}
              negative={testQuerySuccess === false}
            >
              {testQuerySuccess === true
                ? i18next.t("Total Hits: ") + testQueryResult
                : testQueryResult}
              {testQuerySuccess === true && (
                <Message.List>
                  {testQueryHits.map((hit, index) => (
                    <Message.Item key={index}>{hit["metadata"]["title"]}</Message.Item>
                  ))}
                </Message.List>
              )}
            </Message>
          )}
        </Form>
      )}
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
};

CollectionForm.defaultProps = {
  testQueryResult: null,
  testQuerySuccess: null,
  testQueryHits: [],
  error: "",
  slugGeneration: false,
};

export default CollectionForm;
