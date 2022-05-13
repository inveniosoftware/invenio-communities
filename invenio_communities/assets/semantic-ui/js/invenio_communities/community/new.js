/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 * Copyright (C) 2021-2022 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { Formik } from "formik";
import _get from "lodash/get";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import {
  FieldLabel,
  RadioField,
  TextField,
  withCancel,
} from "react-invenio-forms";
import {
  Button,
  Divider,
  Form,
  Grid,
  Header,
  Icon,
  Message,
} from "semantic-ui-react";
import { CommunityApi } from "../api";
import { communityErrorSerializer } from "../api/serializers";

const IdentifierField = ({ formConfig, slug = "" }) => {
  const [newSlug, setNewSlug] = React.useState(slug);

  const helpText = (
    <>
      {i18next.t(
        "This is your community's unique identifier. You will be able to access your community through the URL:"
      )}
      <br />
      {`${formConfig.SITE_UI_URL}/communities/${newSlug}`}
    </>
  );

  return (
    <TextField
      onChange={setNewSlug}
      label={
        <FieldLabel
          htmlFor="slug"
          icon="barcode"
          label={i18next.t("Identifier")}
        />
      }
      fieldPath="slug"
      helpText={helpText}
      fluid
      className="text-muted"
      // Prevent submitting before the value is updated:
      onKeyDown={(e) => { e.key === "Enter" && e.preventDefault()}}
    />
  );
};

class CommunityCreateForm extends Component {
  state = {
    error: "",
  };

  componentWillUnmount() {
    this.cancellableCreate && this.cancellableCreate.cancel();
  }

  setGlobalError = (errorMsg) => {
    this.setState({ error: errorMsg });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    const client = new CommunityApi();
    const payload = {
      metadata: {},
      ...values,
    };
    this.cancellableCreate = withCancel(client.create(payload));

    try {
      const response = await this.cancellableCreate.promise;
      setSubmitting(false);
      window.location.href = response.data.links.settings_html;
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { errors, message } = communityErrorSerializer(error);

      if (message) {
        this.setGlobalError(message);
      }

      if (errors) {
        errors.map(({ field, messages }) => setFieldError(field, messages[0]));
      }
    }
  };

  render() {
    const { formConfig } = this.props;
    const { error } = this.state;

    return (
      <Formik
        initialValues={{
          access: {
            visibility: "public",
          },
          slug: "",
        }}
        onSubmit={this.onSubmit}
      >
        {({ values, isSubmitting, handleSubmit }) => (
          <Form onSubmit={handleSubmit} className="communities-creation">
            <Message
              hidden={error === ""}
              negative
              className="flashed"
            >
              <Grid container>
                <Grid.Column width={15} textAlign="left">
                  <strong>{error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid container centered>
              <Grid.Row>
                <Grid.Column width={8} textAlign="center">
                  <Header className="mt-15" as="h2">
                    {i18next.t("Setup your new community")}
                  </Header>
                  <Divider />
                </Grid.Column>
              </Grid.Row>
              <Grid.Row textAlign="left">
                <Grid.Column width={8}>
                  <TextField
                    fluid
                    fieldPath="metadata.title"
                    // Prevent submitting before the value is updated:
                    onKeyDown={(e) => { e.key === "Enter" && e.preventDefault()}}
                    label={
                      <FieldLabel
                        htmlFor="metadata.title"
                        icon="book"
                        label={i18next.t("Community name")}
                      />
                    }
                  />
                  <IdentifierField
                    formConfig={formConfig}
                    slug={values["slug"]}
                  />
                  <Header as="h3">{i18next.t("Community visibility")}</Header>
                  {formConfig.access.visibility.map((item) => (
                    <React.Fragment key={item.value}>
                      <RadioField
                        key={item.value}
                        fieldPath="access.visibility"
                        label={item.text}
                        labelIcon={item.icon}
                        checked={
                          _get(values, "access.visibility") === item.value
                        }
                        value={item.value}
                        onChange={({ event, data, formikProps }) => {
                          formikProps.form.setFieldValue(
                            "access.visibility",
                            item.value
                          );
                        }}
                      />
                      <label className="helptext">{item.helpText}</label>
                    </React.Fragment>
                  ))}
                </Grid.Column>
              </Grid.Row>
              <Grid.Row>
                <Grid.Column textAlign="center">
                  <Button
                    positive
                    icon
                    labelPosition="left"
                    loading={isSubmitting}
                    disabled={isSubmitting}
                    type="submit"
                  >
                    <Icon name="plus" />
                    {i18next.t("Create community")}
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

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);

ReactDOM.render(<CommunityCreateForm formConfig={formConfig} />, domContainer);
export default CommunityCreateForm;
