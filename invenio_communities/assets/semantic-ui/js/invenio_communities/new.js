/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";
import axios from "axios";
import _ from "lodash";
import { RichInputField } from "./forms";
import { DeleteActionButton } from './fields'
import { Icon, Grid } from "semantic-ui-react";
import { SelectField, TextField } from 'react-invenio-forms';


const renderIdentifiers = ({ arrayPath, indexPath, ...arrayHelpers }) => {
  const path = `${arrayPath}.${indexPath}`; // alternate_identifiers.0
  return (
    <>
      <TextField
        required
        fluid
        label="Scheme"
        fieldPath={`${path}.scheme`}
      />
      <TextField
        basic
        fluid
        fieldPath={`${path}.identifier`}
        label="Identifier"
      />
      <DeleteActionButton deleteClick={() => arrayHelpers.remove(indexPath)} />
    </>
  );
};


const renderFunding = ({ arrayPath, indexPath, ...arrayHelpers }) => {
  return (
    <>
      <TextField
        label="Funding"
        fieldPath={`${arrayPath}.${indexPath}`}
        action={
          <DeleteActionButton
            icon="trash"
            onClick={() => arrayHelpers.remove(indexPath)}
          />
        }
      />
    </>
  );
};


const COMMUNITY_TYPES = [
  { value: "organization", text: "Institution/Organization" },
  { value: "event", text: "Event" },
  { value: "topic", text: "Topic" },
  { value: "project", text: "Project" }
];

const VISIBILITY_TYPES = [
  { value: "public", text: "Public" },
  { value: "private", text: "Private" },
  { value: "hidden", text: "Hidden" }
];

const MEMBER_POLICY_TYPES = [
  { value: "open", text: "Open" },
  { value: "closed", text: "Closed" }
]

const RECORD_POLICY_TYPES = [
  { value: "open", text: "Open" },
  { value: "closed", text: "Closed" },
  { value: "restricted", text: "Restricted" }
];

const CommunityCreateForm = () => {
  const [globalError, setGlobalError] = useState(null);
  const [community, setCommunity] = useState({});

  useEffect(() =>{
    if (!formConfig.is_new){
    var community_id = window.location.pathname.split('/')[2];
    fetch("/api/communities/" + community_id)
      .then(res => res.json())
      .then(
        (result) => { setCommunity(result.metadata); },
        (error) => { },
      )}
      else{
        setCommunity({})
      }
      }, [])
  if (Object.keys(community).length === 0 && !formConfig.is_new){
    return (
      <div className="ui bottom attached loading tab">
        <p></p>
        <p></p>
      </div>
  )
  }
  else{
    return (
      <div className="ui container">
        <Formik
          initialValues={{
            id: community.id || "",
            description: community.description,
            title: community.title || "",
            curation_policy: community.curation_policy || "",
            page: community.page || "",
            type: community.event || "organization",
            website: community.website || "",
            visibility: community.visibility || "public",
            member_policy: community.member_policy || "open",
            record_policy: community.record_policy || "open",
            funding: community.funding || [],
            domains: community.domains || [],
            alternate_identifiers: community.alternate_identifiers || []}}
          validationSchema={Yup.object({
            id: Yup.string()
              .required("Required")
              .max(32, "Must be 32 characters or less"),
            description: Yup.string()
              .required("Required")
              .max(250, "Must be 250 characterdasdass or less"),
            title: Yup.string()
              .max(120, "Must be 120 characters or less")
              .required("Required"),
            curation_policy: Yup.string().max(
              250,
              "Must be 250 characters or less"
            ),
            page: Yup.string().max(250, "Must be 250 characters or less"),
            type: Yup.string()
              .required("Required")
              .oneOf(
                COMMUNITY_TYPES.map(c => {
                  return c.value;
                })
              ),
            visibility: Yup.string()
              .required("Required")
              .oneOf(
                VISIBILITY_TYPES.map(c => {
                  return c.value;
                })
              ),
            website: Yup.string().url("Must be a valid URL"),
            funding: Yup.array().of(Yup.string()
            .max(20, "Must be 20 characters or less")),
            domains: Yup.array().of(Yup.string().oneOf(
              formConfig.domains.map( c => {
                return c.value;
              }))),
            alternate_identifiers: Yup.array().of(Yup.object().shape({
              scheme: Yup.string().max(20, "Must be 20 characters or less"),
              identifier: Yup.string().max(20, "Must be 20 characters or less")
            })),
            record_policy: Yup.string()
              .required("Required")
              .oneOf(
                RECORD_POLICY_TYPES.map( c => {
                  return c.value;
                })
              ),
            member_policy: Yup.string()
              .required("Required")
              .oneOf(
                MEMBER_POLICY_TYPES.map( c => {
                  return c.value;
                })
              ),
          })}
          onSubmit={(values, { setSubmitting, setErrors, setFieldError }) => {
            setSubmitting(true);
            const payload = _.pickBy(values, val => val !== "" && !_.isNil(val));
            if (formConfig.is_new) {
              var request_promise = axios.post("/api/communities/", payload)
            } else {
              var request_promise = axios.put(`/api/communities/${community.id}`, payload)
            }
            request_promise
              .then(response => {
                window.location.href = `/communities/${payload.id}`;
              })
              .catch(error => {
                // TODO: handle nested fields
                if (error.response.data.errors) {
                  error.response.data.errors.map(({ field, message }) =>
                    setFieldError(field, message)
                  );
                } else if (error.response.data.message) {
                  setGlobalError(error.response.data.message);
                }
              })
              .finally(() => setSubmitting(false));
          }}
        >
          {({ values, isSubmitting, isValid }) => (
            <Form>
              <Grid>
                <Grid.Column width={10}>
                {formConfig.is_new ? (
              <h2>Create a community</h2>) : <h2 className="underline">Community Profile</h2>}
              {formConfig.is_new ? (
              <TextField required label='ID' fieldPath="id" fluid />
              ): null}
              <TextField required label="Title" fieldPath="title" fluid />
              <SelectField
                required
                search
                label="Type"
                fieldPath="type"
                options={COMMUNITY_TYPES}
              />
              <RichInputField label="Description" fieldPath="description" fluid/>
              <RichInputField label="Page" fieldPath="page" fluid/>
              <RichInputField label="Curation policy" fieldPath="curation_policy" fluid/>
              <TextField label="Website" fieldPath="website" fluid/>
              {/* <SelectField
                required
                search
                label="Visibility"
                fieldPath="visibility"
                options={VISIBILITY_TYPES}
              /> */}
              {/* <SelectField
                required
                search
                label="Record policy"
                fieldPath="record_policy"
                options={RECORD_POLICY_TYPES}
              /> */}
              {/* <SelectField
                required
                search
                label="Member policy"
                fieldPath="member_policy"
                options={MEMBER_POLICY_TYPES}
              /> */}
              {<SelectField
                required
                search
                label="Domains"
                fieldPath="domains"
                options={formConfig.domains}
                multiple
              />}
              {/* <ArrayField
                fieldPath="alternate_identifiers"
                defaultNewValue={{ scheme: '', identifier: '' }}
                renderArrayItem={renderIdentifiers}
                addButtonLabel="Add alternate identifer"
              /> */}
              {/* <ArrayField
                fieldPath="funding"
                defaultNewValue=""
                renderArrayItem={renderFunding}
                addButtonLabel="Add funding"
              /> */}
              <button
                disabled={!isValid || isSubmitting}
                className="ui positive button small"
                type="submit"
              >
                Submit
              </button>
              {globalError ? (
                <div className="help-block">{globalError}</div>
              ) : null}
                </Grid.Column>
                <Grid.Column width={6}>
              <div className="community-logo-form">
                <Icon name="users" size="massive"></Icon>
                <br></br>
                <button className="ui positive button small">Upload new image</button>
              </div>
                </Grid.Column>
              </Grid>
            </Form>
          )}
        </Formik>
      </div>
    );
  };
}

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);

ReactDOM.render(<CommunityCreateForm />, domContainer);
export default CommunityCreateForm;
