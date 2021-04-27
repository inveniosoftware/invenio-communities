/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React, { Component, useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { Formik } from "formik";
import axios from "axios";
import _defaultsDeep from "lodash/defaultsDeep";

import { Divider, Icon, Grid, Button, Header, Form } from "semantic-ui-react";
import { SelectField } from "react-invenio-forms";

class CommunityPrivilegesForm extends Component {
  getInitialValues = () => {
    let initialValues = _defaultsDeep(this.props.community, {
      access: {
        visibility: "public",
        member_policy: "open",
        record_policy: "open",
      },
    });

    return initialValues;
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
          const payload = values;
          try {
            await axios.put(
              `/api/communities/${this.props.community.id}`,
              payload,
              {
                headers: {
                  Accept: "application/json",
                  "Content-Type": "application/json",
                },
                withCredentials: true,
              }
            );
            setSubmitting(false);
          } catch (error) {
            // TODO: handle nested fields
            //   if (error.response.data.errors) {
            //     error.response.data.errors.map(({ field, message }) =>
            //       setFieldError(field, message)
            //     );
            //   } else if (error.response.data.message) {
            //     setGlobalError(error.response.data.message);
            //   }
            // }
            setSubmitting(false);
          }
        }}
      >
        {({ isSubmitting, handleSubmit }) => (
          <Form onSubmit={handleSubmit}>
            <Grid>
              <Grid.Column width={16}>
                <Header as="h2">Community permissions</Header>
                <Divider />
              </Grid.Column>
              <Grid.Column width={6}>
                <Header as="h3">Community visibility</Header>
                <p>This is a text explaining about the permission</p>
                <SelectField
                  fieldPath="access.visibility"
                  options={this.props.formConfig.access.visibilty}
                />
                <Button
                  compact
                  primary
                  icon
                  labelPosition="left"
                  loading={isSubmitting}
                >
                  <Icon name="save"></Icon>Save
                </Button>
              </Grid.Column>
              {/* Used to clear the row space */}
              <Grid.Column width={10} />
              <Grid.Column width={6}>
                <Header as="h3">Records permissions</Header>
                <p>This is a text explaining about the permission</p>
                <SelectField
                  fieldPath="access.record_policy"
                  options={this.props.formConfig.access.record_policy}
                />
                <Button compact primary icon labelPosition="left">
                  <Icon name="save"></Icon>Save
                </Button>
              </Grid.Column>
              {/* Used to clear the row space */}
              <Grid.Column width={10} />
              <Grid.Column width={6}>
                <Header as="h3">Members permission policy</Header>
                <p>This is a text explaining about the permission</p>
                <SelectField
                  fieldPath="access.member_policy"
                  options={this.props.formConfig.access.member_policy}
                />
                <Button compact primary icon labelPosition="left">
                  <Icon name="save"></Icon>Save
                </Button>
              </Grid.Column>
              {/* Used to clear the row space */}
              <Grid.Column width={10} />
            </Grid>
          </Form>
        )}
      </Formik>
    );
  }
}

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const community = JSON.parse(domContainer.dataset.community);

ReactDOM.render(
  <CommunityPrivilegesForm formConfig={formConfig} community={community} />,
  domContainer
);
export default CommunityPrivilegesForm;
