/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { Formik, Form, FieldArray, Field } from "formik";
import * as Yup from "yup";
import axios from "axios";
import _ from "lodash";
import { TextInput, SelectInput, RichInput, StringArrayInput, ObjectArrayInput } from "./forms";

const COMMUNITY_TYPES = [
  { id: "organization", display: "Institution/Organization" },
  { id: "event", display: "Event" },
  { id: "topic", display: "Topic" },
  { id: "project", display: "Project" }
];

const VISIBILITY_TYPES = [
  { id: "public", display: "Public" },
  { id: "private", display: "Private" },
  { id: "hidden", display: "Hidden" }
];

const MEMBER_POLICY_TYPES = [
  { id: "open", display: "Open" },
  { id: "closed", display: "Closed" }
]

const RECORD_POLICY_TYPES = [
  { id: "open", display: "Open" },
  { id: "closed", display: "Closed" },
  { id: "restricted", display: "Restricted" }
];

const CommunityEditForm = () => {
  const [globalError, setGlobalError] = useState(null);
  const [community, setCommunity] = useState(null);

  useEffect(() =>{
    var community_id = window.location.pathname.split('/')[2];
    fetch("/api/communities/" + community_id)
      .then(res => res.json())
      .then(
        (result) => {
          setCommunity(result.metadata);
        },
        (error) => {
        }
      )
  console.log(community)
      }, [])
  if (!community){
    return ('Give us just a second.')
  }
  else{
    return (
      <div className="container">
        <h1>Modify your community</h1>
        <Formik
          initialValues={{
            id: community.id,
            description: community.description,
            title: community.title || "",
            curation_policy: community.curation_policy || "",
            page: community.page || "",
            type: community.event || "event",
            website: community.website || "",
            visibility: community.visibility || "public",
            member_policy: community.member_policy || "open",
            record_policy: community.record_policy || "open",
            funding: community.funding || [''],
            domain: community.domain || [''],
            alternate_identifiers: community.alternate_identifiers || [{'scheme': '', 'identifier': ''}]
          }}
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
                  return c.id;
                })
              ),
            visibility: Yup.string()
              .required("Required")
              .oneOf(
                VISIBILITY_TYPES.map(c => {
                  return c.id;
                })
              ),
            website: Yup.string().url("Must be a valid URL"),
            funding: Yup.array().of(Yup.string()
            .max(20, "Must be 20 characters or less")),
            domain: Yup.array().of(Yup.string()
            .max(20, "Must be 20 characters or less")),
            alternate_identifiers: Yup.array().of(Yup.string()
              .max(20, "Must be 20 characters or less")),
            record_policy: Yup.string()
              .required("Required")
              .oneOf(
                RECORD_POLICY_TYPES.map( c => {
                  return c.id;
                })
              ),
            member_policy: Yup.string()
              .required("Required")
              .oneOf(
                MEMBER_POLICY_TYPES.map( c => {
                  return c.id;
                })
              ),
          })}
          onSubmit={(values, { setSubmitting, setErrors, setFieldError }) => {
            setSubmitting(true);
            const payload = _.pickBy(values, val => val !== "" && !_.isNil(val));
            axios
              .put(`/api/communities/${community.id}`, payload)
              .then(response => {
                console.log(response);
                window.location.href = "/communities";
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
                console.log(error.response.data);
              })
              .finally(() => setSubmitting(false));
          }}
        >
          {({ values, isSubmitting, isValid }) => (
            <Form>
              <TextInput label="ID" placeholder="biosyslit" name="id" />
              <TextInput label="Title" placeholder="BLR" name="title" />
              <SelectInput choices={COMMUNITY_TYPES} label="Type" name="type" />
              <RichInput label="Description" name="description" />
              <RichInput label="Page" name="page" />
              <RichInput label="Curation policy" name="curation_policy" />
              <TextInput
                label="Website"
                placeholder="https://example.org"
                name="website"
              />
              <SelectInput
                choices={VISIBILITY_TYPES}
                label="Visibility"
                name="visibility"
              />
              <SelectInput
                choices={MEMBER_POLICY_TYPES}
                label="Member policy"
                name="member_policy"
              />
              <SelectInput
                choices={RECORD_POLICY_TYPES}
                label="Record policy"
                name="record_policy"
              />
              <StringArrayInput label="Domain" placeholder="biology" name="domain" />
              <ObjectArrayInput label="Alternate Identifiers" name="alternate_identifiers" keys= "scheme/identifier"/>
              <StringArrayInput label="Funding" name="funding" />
              <button
                disabled={!isValid || isSubmitting}
                className="btn"
                type="submit"
              >
                Submit
              </button>
              {globalError ? (
                <div className="help-block">{globalError}</div>
              ) : null}
            </Form>
          )}
        </Formik>
      </div>
    );
  };
}

ReactDOM.render(<CommunityEditForm />, document.getElementById("app"));

export default CommunityEditForm;
