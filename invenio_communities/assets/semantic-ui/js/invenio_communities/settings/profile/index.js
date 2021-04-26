/*
 * This file is part of Invenio.
 * Copyright (C) 2021 CERN.
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
import Dropzone from "react-dropzone";

import { DeleteButton } from "./DeleteButton";
import { RenameCommunityButton } from "./RenameCommunityButton";

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
  FieldLabel,
  RemoteSelectField,
  RichInputField,
  SelectField,
  TextField,
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

const LogoUploader = (props) => {
  let dropzoneParams = {
    preventDropOnDocument: true,
    onDropAccepted: async (acceptedFiles) => {
      const file = acceptedFiles[0];
      const uploadURL = props.community.links.logo;
      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.put(uploadURL, file, {
        headers: {
          "content-type": "application/octet-stream",
        },
      });
      window.location.reload();
    },
    multiple: false,
    noClick: true,
    noKeyboard: true,
    disabled: false,
  };

  const deleteLogo = async () => {
    const deleteURL = `/api/communities/${props.community.id}/logo`;
    const response = await axios.delete(deleteURL, {
      headers: {
        "content-type": "application/octet-stream",
      },
    });
    props.onImageUpload(response);
  };

  return (
    <Dropzone {...dropzoneParams}>
      {({ getRootProps, getInputProps, open: openFileDialog }) => (
        <Grid.Column width={16}>
          <span {...getRootProps()}>
            <input {...getInputProps()} />
            <Grid>
              <Grid.Column floated="right" width={10}>
                <Grid.Row>
                  <Header className="communities-logo-header">
                    Profile picture
                  </Header>
                </Grid.Row>
                <Grid.Row>
                  {props.logo ? (
                    <Image
                      src={props.logo.links.self}
                      size="medium"
                      wrapped
                      rounded
                    />
                  ) : (
                    <Icon name="users" size="massive" />
                  )}
                </Grid.Row>
                <br />
                <Grid.Row className="logo-buttons">
                  <Button
                    fluid
                    icon
                    labelPosition="left"
                    type="button"
                    onClick={openFileDialog}
                  >
                    <Icon name="upload"></Icon>
                    Upload new picture
                  </Button>
                  {props.logo && (
                    <DeleteButton
                      label="Delete picture"
                      redirectURL={`${props.community.links.self_html}/settings`}
                      confirmationMessage={
                        <h3>Are you sure you want to delete this picture?</h3>
                      }
                      onDelete={() =>
                        axios.delete(props.community.links.logo, {
                          headers: {
                            "content-type": "application/octet-stream",
                          },
                        })
                      }
                    />
                  )}
                </Grid.Row>
              </Grid.Column>
            </Grid>
          </span>
        </Grid.Column>
      )}
    </Dropzone>
  );
};

const DangerZone = (props) => (
  <Grid.Row className="ui message negative danger-zone">
    <Grid.Column width={16}>
      <Header as="h2" color="red">
        Danger zone
      </Header>
      <Divider />
    </Grid.Column>
    <Grid.Column floated="left" width="12">
      <Header as="h4">Rename community</Header>
      <p>
        Here is an explanation of what will happen when you rename a community.
      </p>
    </Grid.Column>
    <Grid.Column floated="right" width="4">
      <RenameCommunityButton community={props.community} />
    </Grid.Column>
    {/* Empty column for margin */}
    <Grid.Column width={16} className="margin-top-25"></Grid.Column>
    <Grid.Column floated="left" width="12">
      <Header as="h4">Delete community</Header>
      <p>
        Here is an explanation of what will happen when you delete a community.
      </p>
    </Grid.Column>
    <Grid.Column floated="right" width="4">
      <DeleteButton
        community={props.community}
        label="Delete community"
        redirectURL="/communities"
        confirmationMessage={
          <h3>Are you sure you want to delete this community?</h3>
        }
        onDelete={() => {
          return axios.delete(
            props.community.links.self,
            {},
            {
              headers: { "Content-Type": "application/json" },
            }
          );
        }}
      />
    </Grid.Column>
  </Grid.Row>
);

class CommunityProfileForm extends Component {
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
      // TODO: should this come from the backend?
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
              <Grid.Row>
                <Grid.Column width={16}>
                  <Header as="h2">{community.id}</Header>
                  <Divider className="no-margin" />
                </Grid.Column>
              </Grid.Row>

              <Grid.Row className="no-padding-tb">
                <Grid.Column width={9}>
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
                    fieldPath="metadata.website"
                    label={
                      <FieldLabel
                        htmlFor="metadata.website"
                        icon="chain"
                        label="Website"
                      />
                    }
                    fluid
                  />
                  <TextField
                    fieldPath="metadata.description"
                    label={
                      <FieldLabel
                        htmlFor="metadata.description"
                        icon={"pencil"}
                        label="Description"
                      />
                    }
                    optimized
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
                  <Button
                    disabled={!isValid || isSubmitting}
                    loading={isSubmitting}
                    labelPosition="left"
                    primary
                    type="submit"
                    icon
                  >
                    <Icon name="save" />
                    Save
                  </Button>
                </Grid.Column>
                <Grid.Column width={7}>
                  <LogoUploader
                    community={this.props.community}
                    logo={this.props.logo}
                  />
                </Grid.Column>
              </Grid.Row>
              <DangerZone community={this.props.community} />
            </Grid>
          </Form>
        )}
      </Formik>
    );
  }
}

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const logo = JSON.parse(domContainer.dataset.logo);

ReactDOM.render(
  <CommunityProfileForm community={community} logo={logo} />,
  domContainer
);
export default CommunityProfileForm;
