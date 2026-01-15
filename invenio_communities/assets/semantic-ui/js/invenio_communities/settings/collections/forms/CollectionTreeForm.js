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

const CollectionTreeForm = ({
  initialValues,
  validationSchema,
  onSubmit,
  handleCancel,
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
        <Form onSubmit={handleSubmit} className="communities-collection-tree">
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
                  includesPaths={["title", "slug"]}
                  label={i18next.t("Basic information")}
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
                          icon="group"
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
                          icon="group"
                          label={i18next.t("Slug")}
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
        </Form>
      )}
    </Formik>
  );
};

CollectionTreeForm.propTypes = {
  initialValues: PropTypes.object.isRequired,
  validationSchema: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  handleCancel: PropTypes.func.isRequired,
  error: PropTypes.string,
  slugGeneration: PropTypes.bool,
};

CollectionTreeForm.defaultProps = {
  error: "",
  slugGeneration: false,
};

export default CollectionTreeForm;
