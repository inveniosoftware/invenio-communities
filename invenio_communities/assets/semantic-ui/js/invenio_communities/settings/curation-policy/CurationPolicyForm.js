/*
 * This file is part of Invenio.
 * Copyright (C) 2023 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { Formik } from "formik";
import _defaultsDeep from "lodash/defaultsDeep";
import React, { Component } from "react";
import { FieldLabel, RichInputField, CKEditorConfig } from "react-invenio-forms";
import { Button, Form, Grid, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "../../api";
import { communityErrorSerializer } from "../../api/serializers";
import PropTypes from "prop-types";
import * as Yup from "yup";

const COMMUNITY_VALIDATION_SCHEMA = Yup.object({
  metadata: Yup.object({
    curation_policy: Yup.string().max(2000, "Maximum number of characters is 2000"),
  }),
});

export class CurationPolicyForm extends Component {
  state = {
    error: "",
  };
  getInitialValues = () => {
    const { community } = this.props;
    let initialValues = _defaultsDeep(community, {
      metadata: {
        curation_policy: "",
      },
    });

    return initialValues;
  };

  setGlobalError = (errorMsg) => {
    this.setState({ error: errorMsg });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    const { community } = this.props;
    setSubmitting(true);

    try {
      const client = new CommunityApi();
      await client.update(community.id, values);
      window.location.reload();
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { message, errors } = communityErrorSerializer(error);

      if (message) {
        this.setGlobalError(message);
      }

      if (errors) {
        errors.forEach(({ field, messages }) => setFieldError(field, messages[0]));
      }
    }

    setSubmitting(false);
  };
  render() {
    const { error } = this.state;
    const { community } = this.props;
    return (
      <Formik
        initialValues={this.getInitialValues(community)}
        validationSchema={COMMUNITY_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
      >
        {({ isSubmitting, isValid, handleSubmit }) => (
          <Form onSubmit={handleSubmit}>
            <Message hidden={error === ""} negative className="flashed">
              <Grid container>
                <Grid.Column width={15} textAlign="left">
                  <strong>{error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid>
              <Grid.Row className="pt-10 pb-0">
                <Grid.Column mobile={16} tablet={16} computer={12} className="rel-pb-2">
                  <RichInputField
                    fieldPath="metadata.curation_policy"
                    label={
                      <FieldLabel
                        htmlFor="metadata.curation_policy"
                        icon="pencil"
                        label={i18next.t("Curation policy")}
                      />
                    }
                    editorConfig={CKEditorConfig}
                    fluid
                  />
                  <Button
                    primary
                    icon
                    labelPosition="left"
                    loading={isSubmitting}
                    disabled={!isValid || isSubmitting}
                    toggle
                    type="submit"
                  >
                    <Icon name="save" />
                    {i18next.t("Save")}
                  </Button>
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Form>
        )}
      </Formik>
    );
  }
}

CurationPolicyForm.propTypes = {
  community: PropTypes.object.isRequired,
};
