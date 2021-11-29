/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component, useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { Formik } from "formik";
import _defaultsDeep from "lodash/defaultsDeep";
import _get from "lodash/get";

import {
  Divider,
  Icon,
  Grid,
  Button,
  Header,
  Form,
  Message,
} from "semantic-ui-react";
import { FieldLabel, RadioField, TextField } from "react-invenio-forms";

import { CommunitiesApiClient } from "./api";


class CommunityCreateForm extends Component {
  state = {
    error: "",
  };
  getInitialValues = () => {
    let initialValues = _defaultsDeep(this.props.community, {
      access: {
        visibility: "public",
      },
    });

    return initialValues;
  };

  setGlobalError = (errorMsg) => {
    this.setState({ error: errorMsg });
  };

  render() {
    return (
      <Formik
        initialValues={this.getInitialValues(this.props.community)}
        onSubmit={async (
          values,
          { setSubmitting, setErrors, setFieldError }
        ) => {
          setSubmitting(true);
          const client = new CommunitiesApiClient();
          const payload = {
            "metadata": {},
            ...values
          }
          const response = await client.create(payload);
          setSubmitting(false);
          if (response.code < 400) {
            window.location.href = response.data.links.settings_html;
          } else {
            if (response.errors) {
              response.errors.map(({ field, messages }) =>
                setFieldError(field, messages[0])
              );
            }

            if (response.data.message) {
              this.setGlobalError(response.data.message);
            }
          }
        }}
      >
        {({ values, isSubmitting, handleSubmit }) => (
          <Form onSubmit={handleSubmit} className="communities-creation">
            <Message
              hidden={this.state.error == ""}
              negative
              className="flashed top-attached"
            >
              <Grid container>
                <Grid.Column width={15} textAlign="left">
                  <strong>{this.state.error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid container centered>
              <Grid.Row>
                <Grid.Column width={8} textAlign="center">
                  <Header as="h2">Setup your new community</Header>
                  <Divider />
                </Grid.Column>
              </Grid.Row>
              <Grid.Row textAlign="left">
                <Grid.Column width={8}>
                  <TextField
                    fluid
                    fieldPath="metadata.title"
                    label={
                      <FieldLabel
                        htmlFor="metadata.title"
                        icon={"book"}
                        label="Community name"
                      />
                    }
                  />
                  <TextField
                    label="Identifier"
                    fieldPath="id"
                    helpText={`This is your community's unique identifier. You will be able to access your community
                    through the URL: ${
                      this.props.formConfig.SITE_UI_URL
                    }/communities/${_get(values, "id", "")}`}
                    fluid
                    className="communities-identifier"
                  />
                  <Header as="h3">Community visibility</Header>
                  {this.props.formConfig.access.visibilty.map((item) => (
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
                    type="submit"
                  >
                    <Icon name="plus"></Icon>Create community
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
