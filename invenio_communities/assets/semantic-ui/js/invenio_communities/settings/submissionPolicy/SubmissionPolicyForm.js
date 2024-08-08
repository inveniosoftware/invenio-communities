/*
 * This file is part of Invenio.
 * Copyright (C) 2023 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { useField } from "formik";
import { CommunitySettingsForm } from "../components";
import _get from "lodash/get";
import React, { Component } from "react";
import { RadioField } from "react-invenio-forms";
import { Header } from "semantic-ui-react";
import PropTypes from "prop-types";

const ReviewPolicyField = ({ label, formConfig, ...props }) => {
  const [field] = useField(props);
  return (
    <>
      {formConfig.access.review_policy.map((item) => (
        <React.Fragment key={item.value}>
          <RadioField
            key={item.value}
            fieldPath="access.review_policy"
            label={item.text}
            aria-label={item.text}
            labelIcon={item.icon}
            checked={_get(field.value, "access.review_policy") === item.value}
            value={item.value}
          />
          <label className="helptext">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

ReviewPolicyField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

ReviewPolicyField.defaultProps = {
  label: "",
};

const RecordSubmissionPolicyField = ({ label, formConfig, ...props }) => {
  const [field] = useField(props);
  const fieldPath = "access.record_submission_policy";
  const { record_submission_policy: subPolicy } = formConfig.access;
  return (
    <>
      {subPolicy.map((item) => (
        <React.Fragment key={item.value}>
          <RadioField
            key={item.value}
            fieldPath={fieldPath}
            label={item.text}
            labelIcon={item.icon}
            checked={_get(field.value, fieldPath) === item.value}
            value={item.value}
          />
          <label className="helptext">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

RecordSubmissionPolicyField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

RecordSubmissionPolicyField.defaultProps = {
  label: "",
};

class SubmissionPolicyForm extends Component {
  getInitialValues = () => {
    return {
      access: {
        review_policy: "closed",
        record_submission_policy: "open",
      },
    };
  };

  render() {
    const { community, formConfig } = this.props;
    return (
      <CommunitySettingsForm
        initialValues={this.getInitialValues()}
        community={community}
      >
        <Header as="h2" size="small">
          {i18next.t("Review policy")}
          <Header.Subheader className="mt-5">
            {i18next.t("Controls who can publish records directly without review.")}
          </Header.Subheader>
        </Header>
        <ReviewPolicyField formConfig={formConfig} />

        <Header as="h2" size="small">
          {i18next.t("Records submission policy")}
          <Header.Subheader className="mt-5">
            {i18next.t("Controls who can submit records to the community.")}
          </Header.Subheader>
        </Header>
        <RecordSubmissionPolicyField formConfig={formConfig} />
      </CommunitySettingsForm>
    );
  }
}

SubmissionPolicyForm.propTypes = {
  community: PropTypes.object.isRequired,
  formConfig: PropTypes.object.isRequired,
};

export default SubmissionPolicyForm;
