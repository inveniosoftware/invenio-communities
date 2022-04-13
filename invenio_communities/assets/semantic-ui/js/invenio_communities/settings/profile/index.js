/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import ReactDOM from "react-dom";
import { Formik, getIn } from "formik";
import * as Yup from "yup";
import _unset from "lodash/unset";
import _defaultsDeep from "lodash/defaultsDeep";
import _get from "lodash/get";
import _map from "lodash/map";
import _mapValues from "lodash/mapValues";
import _find from "lodash/find";
import _cloneDeep from "lodash/cloneDeep";
import _isNumber from "lodash/isNumber";
import _isBoolean from "lodash/isBoolean";
import _isEmpty from "lodash/isEmpty";
import _isObject from "lodash/isObject";
import _isArray from "lodash/isArray";
import _isNull from "lodash/isNull";
import _pickBy from "lodash/pickBy";
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
  Message,
  Segment,
} from "semantic-ui-react";
import {
  FieldLabel,
  RemoteSelectField,
  SelectField,
  TextField,
} from "react-invenio-forms";
import { CommunityApi } from "../../api";
import { i18next } from "@translations/invenio_communities/i18next";
import { communityErrorSerializer } from "../../api/serializers";

const COMMUNITY_VALIDATION_SCHEMA = Yup.object({
  metadata: Yup.object({
    title: Yup.string().max(
      250,
      i18next.t("Maximum number of characters is 2000")
    ),
    description: Yup.string().max(
      2000,
      i18next.t("Maximum number of characters is 2000")
    ),
    website: Yup.string().url(i18next.t("Must be a valid URL")),
    type: Yup.object().shape({
      id: Yup.string(),
    }),
    // TODO: Re-enable once properly integrated to be displayed
    // page: Yup.string().max(2000, "Maximum number of characters is 2000"),
    // curation_policy: Yup.string().max(
    //   2000,
    //   "Maximum number of characters is 2000"
    // ),
  }),
});

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
      const formData = new FormData();
      formData.append("file", file);

      try {
        const client = new CommunityApi();
        await client.updateLogo(props.community.id, file);
        window.location.reload();
      } catch (error) {
        props.onError(error);
      }
    },
    onDropRejected: (rejectedFiles) => {
      // TODO: show error message when files are rejected e.g size limit
      console.error(rejectedFiles[0].errors);
    },
    multiple: false,
    noClick: true,
    noDrag: true,
    noKeyboard: true,
    disabled: false,
    maxFiles: 1,
    maxSize: 5000000, // 5Mb limit
    accept: ".jpeg,.jpg,.png",
  };

  let deleteLogo = async () => {
    const client = new CommunityApi();
    await client.deleteLogo(props.community.id);
  };

  return (
    <Dropzone {...dropzoneParams}>
      {({ getRootProps, getInputProps, open: openFileDialog }) => (
        <span {...getRootProps()}>
          <input {...getInputProps()} />
          <Header className="mt-0">{i18next.t("Profile picture")}</Header>
          {props.logo ? (
            <Image src={props.logo.links.self} fluid wrapped rounded />
          ) : (
            <Image src={props.defaultLogo} fluid wrapped rounded />
          )}
          <Divider hidden />
          <Button
            fluid
            icon
            labelPosition="left"
            type="button"
            onClick={openFileDialog}
          >
            <Icon name="upload" />
            {i18next.t("Upload new picture")}
          </Button>
          {props.logo && (
            <DeleteButton
              label={i18next.t("Delete picture")}
              redirectURL={`${props.community.links.self_html}/settings`}
              confirmationMessage={
                <h3>
                  {i18next.t("Are you sure you want to delete this picture?")}
                </h3>
              }
              onDelete={deleteLogo}
              onError={props.onError}
            />
          )}
        </span>
      )}
    </Dropzone>
  );
};

const DangerZone = ({ community, onError }) => (
  <Segment color="red" className="rel-mt-2">
    <Header as="h2" color="red">
      {i18next.t("Danger zone")}
    </Header>
    <Grid>
      <Grid.Column width="12">
        <Header as="h4">{i18next.t("Rename community")}</Header>
        <p>
          {i18next.t(
            "Renaming your community can have unintended side effects."
          )}
        </p>
      </Grid.Column>
      <Grid.Column floated="right" width="4">
        <RenameCommunityButton community={community} />
      </Grid.Column>
      <Grid.Column floated="left" width="12">
        <Header as="h4">{i18next.t("Delete community")}</Header>
        <p>
          {i18next.t(
            "Once deleted, it will be gone forever. Please be certain."
          )}
        </p>
      </Grid.Column>
      <Grid.Column floated="right" width="4">
        <DeleteButton
          community={community}
          label={i18next.t("Delete community")}
          redirectURL="/communities"
          confirmationMessage={
            <h3>
              {i18next.t("Are you sure you want to delete this community?")}
            </h3>
          }
          onDelete={async () => {
            const client = new CommunityApi();
            await client.delete(community.id);
          }}
          onError={onError}
        />
      </Grid.Column>
    </Grid>
  </Segment>
);

class CommunityProfileForm extends Component {
  state = {
    error: "",
  };

  /**
   * Object stores known organizations, so that an organization's name can be mapped to it's ID (if known).
   */
  knownOrganizations = {};

  getInitialValues = () => {
    let initialValues = _defaultsDeep(this.props.community, {
      id: "",
      metadata: {
        description: "",
        title: "",
        // TODO: Re-enable once properly integrated to be displayed
        // curation_policy: "",
        // page: "",
        type: {},
        website: "",
        organizations: [],
      },
      // TODO: should this come from the backend?
      access: {
        visibility: "public",
        member_policy: "open",
        record_policy: "open",
      },
    });

    // Deserialise organisations. Store known communities.
    const organizations = [];
    initialValues.metadata.organizations.map((org) => {
      if (org.id) {
        this.knownOrganizations[org.name] = org.id;
      }
      organizations.push(org.name);
    })

    _unset(initialValues, "metadata.type.title");

    return {
      ...initialValues,
      metadata: { ...initialValues.metadata, organizations },
    };
  };

  serializeValues = (values) => {
    let submittedCommunity = _cloneDeep(values);

    // Serialize organisations. If it is known and has an id, serialize a pair 'id/name'. Otherwise use 'name' only
    const organizations = submittedCommunity.metadata.organizations.map(
      (organization) => {
        const orgID = this.knownOrganizations[organization];
        return {
          ...(orgID && {id: orgID}),
          name: organization
        };
      }
    );

    submittedCommunity = {
      ...submittedCommunity,
      metadata: { ...values.metadata, organizations },
    };

    // Clean values
    submittedCommunity = removeEmptyValues(submittedCommunity);

    return submittedCommunity;
  };

  setGlobalError = (error) => {
    const { message } = communityErrorSerializer(error);
    this.setState({ error: message });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    const payload = this.serializeValues(values);
    const client = new CommunityApi();

    try {
      await client.update(this.props.community.id, payload);
      window.location.reload();
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
    }
  };

  render() {
    return (
      <Formik
        initialValues={this.getInitialValues(this.props.community)}
        validationSchema={COMMUNITY_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
      >
        {({ isSubmitting, isValid, handleSubmit }) => (
          <Form onSubmit={handleSubmit} className="communities-profile">
            <Message
              hidden={this.state.error === ""}
              negative
              className="flashed top attached"
            >
              <Grid container>
                <Grid.Column width={15} textAlign="left">
                  <strong>{this.state.error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid>
              <Grid.Row>
                <Grid.Column width={16}>
                  <Header as="h2">{community.id}</Header>
                  <Divider />
                </Grid.Column>
              </Grid.Row>

              <Grid.Row className="pt-0 pb-0">
                <Grid.Column width={9}>
                  <TextField
                    fluid
                    fieldPath="metadata.title"
                    label={
                      <FieldLabel
                        htmlFor="metadata.title"
                        icon={"book"}
                        label={i18next.t("Community name")}
                      />
                    }
                  />
                  <SelectField
                    search
                    clearable
                    fieldPath="metadata.type.id"
                    label={
                      <FieldLabel
                        htmlFor="metadata.type.id"
                        icon="tag"
                        label={i18next.t("Type")}
                      />
                    }
                    options={this.props.commTypes.map((ct) => {
                      return {
                        value: ct.id,
                        text: ct?.title?.en ?? ct.id
                      }
                    })}
                  />
                  <TextField
                    fieldPath="metadata.website"
                    label={
                      <FieldLabel
                        htmlFor="metadata.website"
                        icon="chain"
                        label={i18next.t("Website")}
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
                        label={i18next.t("Description")}
                      />
                    }
                    optimized
                  />
                  <RemoteSelectField
                    fieldPath={"metadata.organizations"}
                    suggestionAPIUrl="/api/affiliations"
                    suggestionAPIHeaders={{
                      Accept: "application/json",
                    }}
                    placeholder={i18next.t(
                      "Search for an organization by name"
                    )}
                    clearable
                    multiple
                    initialSuggestions={_get(
                      this.props.community,
                      "metadata.organizations",
                      []
                    )}
                    serializeSuggestions={(organizations) =>
                      _map(organizations, (organization) =>
                      {
                        const isKnownOrg = this.knownOrganizations.hasOwnProperty(organization.name);
                        if (!isKnownOrg) {
                          this.knownOrganizations = {
                            ...this.knownOrganizations,
                            [organization.name]: organization.id
                          };
                        }
                        return {
                          text: organization.name,
                          value: organization.name,
                          key: organization.name
                        }
                      })
                    }
                    label={i18next.t("Organizations")}
                    noQueryMessage={i18next.t("Search for organizations...")}
                    allowAdditions
                    search={(filteredOptions, searchQuery) => filteredOptions}
                  />
                  {/* TODO: Re-enable once properly integrated to be displayed */}
                  {/* <RichInputField
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
                  /> */}
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
                </Grid.Column>
                <Grid.Column width={4} floated="right">
                  <LogoUploader
                    community={this.props.community}
                    logo={this.props.logo}
                    defaultLogo={this.props.defaultLogo}
                    onError={this.setGlobalError}
                  />
                </Grid.Column>
              </Grid.Row>
              <Grid.Row className="danger-zone">
                <Grid.Column width={16}>
                  <DangerZone
                    community={this.props.community}
                    onError={this.setGlobalError}
                  />
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
const community = JSON.parse(domContainer.dataset.community);
const logo = JSON.parse(domContainer.dataset.logo);
const commTypes = JSON.parse(domContainer.dataset.comtypes);

ReactDOM.render(
  <CommunityProfileForm
    community={community}
    logo={logo}
    defaultLogo="/static/images/square-placeholder.png"
    commTypes={commTypes}
  />,
  domContainer
);
export default CommunityProfileForm;
