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
import * as Yup from "yup";
import axios from "axios";
import _defaultsDeep from "lodash/defaultsDeep";
import _isNil from "lodash/isNil";
import _get from "lodash/get";
import _map from "lodash/map";
import _mapValues from "lodash/mapValues";
import _find from "lodash/find";
import _cloneDeep from "lodash/cloneDeep";
import _set from "lodash/set";
import _isNumber from "lodash/isNumber";
import _isBoolean from "lodash/isBoolean";
import _isEmpty from "lodash/isEmpty";
import _isObject from "lodash/isObject";
import _isArray from "lodash/isArray";
import _isNull from "lodash/isNull";
import _pickBy from "lodash/pickBy";
import _pick from "lodash/pick";

import { DeleteCommunityButton } from "./DeleteCommunityButton";

import {
  Divider,
  Icon,
  Image,
  Grid,
  Button,
  Header,
  Form,
} from "semantic-ui-react";
import {
  SelectField,
  TextField,
  FieldLabel,
  RemoteSelectField,
  RichInputField,
} from "react-invenio-forms";

// TODO: remove when type becomes a vocabulary
const COMMUNITY_TYPES = [
  { value: "organization", text: "Institution/Organization" },
  { value: "event", text: "Event" },
  { value: "topic", text: "Topic" },
  { value: "project", text: "Project" },
];

const COMMUNITY_VALIDATION_SCHEMA = Yup.object({
  metadata: Yup.object({
    title: Yup.string().max(250, "Maximum number of characters is 2000"),
    description: Yup.string().max(2000, "Maximum number of characters is 2000"),
    website: Yup.string().url("Must be a valid URL"),
    page: Yup.string().max(2000, "Maximum number of characters is 2000"),
    curation_policy: Yup.string().max(
      2000,
      "Maximum number of characters is 2000"
    ),
  }),
});

const CKEditorConfig = {
  removePlugins: [
    "Image",
    "ImageCaption",
    "ImageStyle",
    "ImageToolbar",
    "ImageUpload",
    "MediaEmbed",
    "Table",
    "TableToolbar",
    "TableProperties",
    "TableCellProperties",
  ],
};

/**
 * Remove empty fields from community
 * Copied from react-invenio-deposit
 * @method
 * @param {object} obj - potentially empty object
 * @returns {object} community - without empty fields
 */
const removeEmptyValues = (obj) => {
  if (_isArray(obj)) {
    let mappedValues = obj.map((value) => removeEmptyValues(value));
    let filterValues = mappedValues.filter((value) => {
      if (_isBoolean(value) || _isNumber(value)) {
        return value;
      }
      return !_isEmpty(value);
    });
    return filterValues;
  } else if (_isObject(obj)) {
    let mappedValues = _mapValues(obj, (value) => removeEmptyValues(value));
    let pickedValues = _pickBy(mappedValues, (value) => {
      if (_isArray(value) || _isObject(value)) {
        return !_isEmpty(value);
      }
      return !_isNull(value);
    });
    return pickedValues;
  }
  return _isNumber(obj) || _isBoolean(obj) || obj ? obj : null;
};

class CommunityCreateForm extends Component {
  getInitialValues = () => {
    let initialValues = _defaultsDeep(this.props.community, {
      id: "",
      metadata: {
        description: "",
        title: "",
        curation_policy: "",
        page: "",
        type: "organization",
        website: "",
        affiliations: [],
      },
      access: {
        visibility: "public",
        member_policy: "open",
        record_policy: "open",
      },
    });

    // Deserialize affiliations
    let affiliations = _map(
      _get(initialValues, "metadata.affiliations"),
      "name"
    );
    return {
      ...initialValues,
      metadata: { ...initialValues.metadata, affiliations },
    };
  };

  serializeValues = (values) => {
    let submittedCommunity = _cloneDeep(values);
    const findField = (arrayField, key, value) => {
      const knownField = _find(arrayField, {
        [key]: value,
      });
      return knownField ? knownField : { [key]: value };
    };

    const affiliationsFieldPath = "metadata.affiliations";
    const initialAffilliations = _get(
      this.props.community,
      affiliationsFieldPath,
      []
    );
    const affiliations = submittedCommunity.metadata.affiliations.map(
      (affiliation) => {
        return findField(initialAffilliations, "name", affiliation);
      }
    );

    submittedCommunity = {
      ...submittedCommunity,
      metadata: { ...values.metadata, affiliations },
    };

    // Clean values
    submittedCommunity = removeEmptyValues(submittedCommunity);

    return submittedCommunity;
  };

  render() {
    return (
      <Formik
        initialValues={this.getInitialValues(this.props.community)}
        validationSchema={COMMUNITY_VALIDATION_SCHEMA}
        onSubmit={async (
          values,
          { setSubmitting, setErrors, setFieldError }
        ) => {
          setSubmitting(true);
          const payload = this.serializeValues(values);
          try {
            const response = await axios.put(
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
            window.location.href = `/communities/${response.data.id}`;
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
        {({ isSubmitting, isValid, handleSubmit }) => (
          <Form onSubmit={handleSubmit} className="communities-profile">
            <Grid>
              <Grid.Column width={16}>
                <Header as="h2">Community Profile</Header>
                <Divider />
              </Grid.Column>

              <Grid.Row>
                <Grid.Column width={10}>
                  <TextField
                    fluid
                    fieldPath="metadata.title"
                    label={
                      <FieldLabel
                        htmlFor="metadata.title"
                        icon={"book"}
                        label="Display name"
                      />
                    }
                  />
                  <TextField
                    label="Identifier"
                    fieldPath="id"
                    fluid
                    className="communities-identifier"
                  />
                  <SelectField
                    search
                    fieldPath="metadata.type"
                    label={
                      <FieldLabel
                        htmlFor="metadata.type"
                        icon="tag"
                        label="Type"
                      />
                    }
                    options={COMMUNITY_TYPES}
                  />
                  <TextField
                    label="Website url"
                    fieldPath="metadata.website"
                    fluid
                  />
                  <RichInputField
                    fieldPath="metadata.description"
                    label={
                      <FieldLabel
                        htmlFor="metadata.description"
                        icon={"pencil"}
                        label="Description"
                      />
                    }
                    editorConfig={CKEditorConfig}
                    fluid
                    optimized
                  />
                  <RichInputField
                    label="Curation policy"
                    fieldPath="metadata.curation_policy"
                    label={
                      <FieldLabel
                        htmlFor="metadata.curation_policy"
                        icon={"pencil"}
                        label="Curation policy"
                      />
                    }
                    editorConfig={CKEditorConfig}
                    fluid
                  />
                  <RichInputField
                    fieldPath="metadata.page"
                    label={
                      <FieldLabel
                        htmlFor="metadata.page"
                        icon={"pencil"}
                        label="Page description"
                      />
                    }
                    editorConfig={CKEditorConfig}
                    fluid
                  />
                  <RemoteSelectField
                    fieldPath={"metadata.affiliations"}
                    suggestionAPIUrl="/api/vocabularies/affiliations"
                    suggestionAPIHeaders={{
                      Accept: "application/vnd.inveniordm.v1+json",
                    }}
                    placeholder={"Search for an affiliation by name"}
                    clearable
                    multiple
                    initialSuggestions={_get(
                      this.props.community,
                      "metadata.affiliations",
                      []
                    )}
                    serializeSuggestions={(affiliations) =>
                      _map(affiliations, (affiliation) => ({
                        text: affiliation.name,
                        value: affiliation.name,
                        key: affiliation.name,
                      }))
                    }
                    label="Affiliations"
                    noQueryMessage="Search for affiliations..."
                    allowAdditions
                  />
                  <Button
                    disabled={!isValid || isSubmitting}
                    loading={isSubmitting}
                    labelPosition="left"
                    positive
                    type="submit"
                    icon
                  >
                    <Icon name="save" />
                    Save
                  </Button>
                </Grid.Column>
                <Grid.Column width={6}>
                  <Grid relaxed>
                    <Grid.Column floated="right" width={10} textAlign="left">
                      <Grid.Row>
                        <Header>Profile picture</Header>
                      </Grid.Row>
                      <Grid.Row>
                        {this.props.community.files ? (
                          <Image src={this.props.community.files} wrapped />
                        ) : (
                          <Icon name="users" size="massive" />
                        )}
                      </Grid.Row>
                      <Grid.Row>
                        <Button primary>Upload new image</Button>
                      </Grid.Row>
                    </Grid.Column>
                  </Grid>
                </Grid.Column>
              </Grid.Row>
              <Grid.Column width={16} className="danger-zone">
                <Header as="h2" color="red">
                  Danger zone
                </Header>
                <Divider />
              </Grid.Column>
              <Grid.Row>
                <Grid.Column floated="left" width="12">
                  <Header as="h4">Delete community</Header>
                  <p>Do you want to delete the community?</p>
                </Grid.Column>
                <Grid.Column floated="right" width="4">
                  <DeleteCommunityButton community={this.props.community} />
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
const community = JSON.parse(domContainer.dataset.community);

ReactDOM.render(
  <CommunityCreateForm formConfig={formConfig} community={community} />,
  domContainer
);
export default CommunityCreateForm;
