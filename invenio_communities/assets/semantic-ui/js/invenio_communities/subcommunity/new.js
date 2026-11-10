/*
 * SPDX-FileCopyrightText: 2024 CERN.
 * SPDX-FileCopyrightText: 2026 Ubiquity Press.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import { i18next } from "@translations/invenio_communities/i18next";
import { Formik, useFormikContext } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import { Component, Fragment } from "react";
import {
  FieldLabel,
  RadioField,
  RemoteSelectField,
  TextField,
  withCancel,
} from "react-invenio-forms";
import { Button, Divider, Form, Grid, Header, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "../api";
import { communityErrorSerializer } from "../api/serializers";
import Overridable, { OverridableContext, overrideStore } from "react-overridable";

const IdentifierField = ({ formConfig }) => {
  const { values } = useFormikContext();

  const helpText = (
    <>
      {i18next.t(
        "This is your community's unique identifier. You will be able to access your community through the URL:"
      )}
      <br />
      {`${formConfig.SITE_UI_URL}/communities/${values["metadata"]["slug"]}`}
    </>
  );

  return (
    <TextField
      required
      id="metadata.slug"
      label={
        <FieldLabel
          htmlFor="metadata.slug"
          icon="barcode"
          label={i18next.t("Identifier")}
        />
      }
      fieldPath="metadata.slug"
      helpText={helpText}
      fluid
      className="text-muted"
      // Prevent submitting before the value is updated:
      onKeyDown={(e) => {
        e.key === "Enter" && e.preventDefault();
      }}
    />
  );
};

IdentifierField.propTypes = {
  formConfig: PropTypes.object.isRequired,
};

// Hierarchies are one level deep: communities that already have a parent, or
// that allow children (even with none yet), can't become subcommunities.
const ELIGIBLE_COMMUNITIES_QUERY = "NOT _exists_:parent.id AND NOT children.allow:true";

// Characters with special meaning in OpenSearch query string syntax.
const QUERY_STRING_SPECIAL_CHARS = /[+\-=&|><!(){}[\]^"~*?:\\/]/g;

const buildCommunitiesQuery = (searchQuery) => {
  const terms = (searchQuery || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((term) => `${term.replace(QUERY_STRING_SPECIAL_CHARS, "\\$&")}*`);
  if (terms.length === 0) {
    return ELIGIBLE_COMMUNITIES_QUERY;
  }
  return `(${terms.join(" AND ")}) AND ${ELIGIBLE_COMMUNITIES_QUERY}`;
};

const serializeCommunities = (communities) =>
  communities.map((community) => ({
    text: community.metadata.title,
    value: community.id,
    key: community.id,
  }));

class CommunityCreateForm extends Component {
  state = {
    error: "",
    hasCommunity: false,
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
    const { hasCommunity } = this.state;
    const { community } = this.props;
    let payload = {};
    let slug = "";
    if (hasCommunity) {
      payload = { community_id: values["metadata"]["community"] };
    } else {
      slug = values["metadata"]["slug"];
      payload = {
        community: {
          title: values["metadata"]["title"],
          slug: slug,
        },
      };
    }
    this.cancellableCreate = withCancel(
      client.createSubcommunity(community.id, payload)
    );

    try {
      const response = await this.cancellableCreate.promise;
      setSubmitting(false);
      const requestID = response.data.id;
      // TODO this should redirect to the request page as returned by the API.
      // TODO It is computed for now because the link contains references to two different entities (request and community), and that's not supported yet by the backend.
      window.location.href = `/communities/${community.slug}/requests/${requestID}`;
    } catch (error) {
      if (error === "UNMOUNTED") return;

      setSubmitting(false);
      const { errors, message } = communityErrorSerializer(error);

      if (message) {
        this.setGlobalError(
          "The form contains errors or missing fields. Please verify before submitting"
        );
      }

      if (errors) {
        errors.forEach(({ field, messages }) => {
          // Check if the field is already prefixed with "metadata"
          if (!field.startsWith("metadata")) {
            // Add "metadata" prefix if not already present
            field = `metadata.${field.split(".").pop()}`;
          }
          setFieldError(field, messages[0]);
        });
      }
    }
  };

  render() {
    const { formConfig, canCreateRestricted, community } = this.props;
    const { hasCommunity, error } = this.state;

    return (
      <Overridable
        id="InvenioCommunities.CommunityCreateForm.layout"
        formConfig={formConfig}
        canCreateRestricted={canCreateRestricted}
        error={error}
        community={community}
        IdentifierField={IdentifierField}
      >
        <Formik
          initialValues={{
            access: {
              visibility: "public",
            },
            community: {
              slug: "",
              title: "",
            },
            metadata: {
              slug: "",
            },
          }}
          onSubmit={this.onSubmit}
        >
          {({ values, isSubmitting, handleSubmit }) => (
            <Form onSubmit={handleSubmit} className="communities-creation">
              <Message hidden={error === ""} negative className="flashed">
                <Grid container centered>
                  <Grid.Column mobile={16} tablet={12} computer={8} textAlign="left">
                    <strong>{error}</strong>
                  </Grid.Column>
                </Grid>
              </Message>
              <Grid container centered>
                <Grid.Row>
                  <Grid.Column mobile={16} tablet={12} computer={8} textAlign="center">
                    <Header as="h1" className="rel-mt-2">
                      {i18next.t("Subcommunity request")}
                    </Header>
                    <Divider />
                  </Grid.Column>
                </Grid.Row>
                <Grid.Row textAlign="left">
                  <Grid.Column mobile={16} tablet={12} computer={8}>
                    <div className="field">
                      <Form.Field>
                        {i18next.t("Do you already have an existing community?")}
                      </Form.Field>
                      <Form.Group>
                        <RadioField
                          label={i18next.t("Yes")}
                          checked={hasCommunity === true}
                          value={i18next.t("Yes")}
                          onChange={() => {
                            this.setState({ hasCommunity: true });
                          }}
                          fieldPath="metadata.hasCommunity"
                        />
                        <RadioField
                          label={i18next.t("No")}
                          checked={hasCommunity === false}
                          value={i18next.t("No")}
                          onChange={() => {
                            this.setState({ hasCommunity: false });
                          }}
                          fieldPath="metadata.hasCommunity"
                        />
                      </Form.Group>
                    </div>
                    {hasCommunity && (
                      <RemoteSelectField
                        label={
                          <FieldLabel
                            icon="user"
                            label={i18next.t("Community")}
                            id="community-label"
                            class="block"
                          />
                        }
                        fieldPath="metadata.community"
                        suggestionAPIUrl="/api/user/communities"
                        suggestionAPIQueryParams={{ sort: "newest" }}
                        searchQueryParamName="q"
                        preSearchChange={buildCommunitiesQuery}
                        serializeSuggestions={serializeCommunities}
                        placeholder={i18next.t("Search for one of your communities")}
                        noQueryMessage={i18next.t("Search for one of your communities")}
                        noResultsMessage={i18next.t("No eligible communities found.")}
                        clearable
                        required
                      />
                    )}
                    {!hasCommunity && (
                      <>
                        <TextField
                          required
                          id="metadata.title"
                          fluid
                          fieldPath="metadata.title"
                          // Prevent submitting before the value is updated:
                          onKeyDown={(e) => {
                            e.key === "Enter" && e.preventDefault();
                          }}
                          label={
                            <FieldLabel
                              htmlFor="metadata.title"
                              icon="book"
                              label={i18next.t("Community name")}
                            />
                          }
                        />
                        <IdentifierField formConfig={formConfig} />
                      </>
                    )}
                    {canCreateRestricted && (
                      <>
                        <Header as="h3">{i18next.t("Community visibility")}</Header>
                        {formConfig.access.visibility.map((item) => (
                          <Fragment key={item.value}>
                            <RadioField
                              key={item.value}
                              fieldPath="access.visibility"
                              label={item.text}
                              labelIcon={item.icon}
                              checked={_get(values, "access.visibility") === item.value}
                              value={item.value}
                              onChange={({ event, data, formikProps }) => {
                                formikProps.form.setFieldValue(
                                  "access.visibility",
                                  item.value
                                );
                              }}
                            />
                            <label className="helptext">{item.helpText}</label>
                          </Fragment>
                        ))}
                      </>
                    )}
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
                      type="button"
                      onClick={(event) => handleSubmit(event)}
                    >
                      <Icon name="plus" />
                      {hasCommunity
                        ? i18next.t("Create request")
                        : i18next.t("Create community")}
                    </Button>
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Form>
          )}
        </Formik>
      </Overridable>
    );
  }
}

CommunityCreateForm.propTypes = {
  formConfig: PropTypes.object.isRequired,
  canCreateRestricted: PropTypes.bool.isRequired,
  community: PropTypes.object.isRequired,
};

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const canCreateRestricted = JSON.parse(domContainer.dataset.canCreateRestricted);
const community = JSON.parse(domContainer.dataset.community);

const overriddenComponents = overrideStore.getAll();
const root = createRoot(domContainer);

root.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CommunityCreateForm
      formConfig={formConfig}
      canCreateRestricted={canCreateRestricted}
      community={community}
    />
  </OverridableContext.Provider>
);

export default CommunityCreateForm;
