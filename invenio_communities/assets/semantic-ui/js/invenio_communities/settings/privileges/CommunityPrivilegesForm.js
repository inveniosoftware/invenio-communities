/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2024 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { CommunitySettingsForm } from "..//components/CommunitySettingsForm";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import { useField } from "formik";
import React, { Component } from "react";
import { RadioField } from "react-invenio-forms";
import { Header } from "semantic-ui-react";
import PropTypes from "prop-types";

const VisibilityField = ({ label, formConfig, ...props }) => {
  const [field] = useField(props);
  const fieldPath = "access.visibility";

  function createHandleChange(radioValue) {
    function handleChange({ event, data, formikProps }) {
      formikProps.form.setFieldValue(fieldPath, radioValue);
      // dependent fields
      if (radioValue === "restricted") {
        formikProps.form.setFieldValue("access.member_policy", "closed");
      }
    }
    return handleChange;
  }

  return (
    <>
      {formConfig.access.visibility.map((item) => (
        <React.Fragment key={item.value}>
          <RadioField
            key={item.value}
            fieldPath={fieldPath}
            label={item.text}
            labelIcon={item.icon}
            checked={_get(field.value, fieldPath) === item.value}
            value={item.value}
            onChange={createHandleChange(item.value)}
          />
          <label className="helptext">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

VisibilityField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

VisibilityField.defaultProps = {
  label: "",
};

const MembersVisibilityField = ({ label, formConfig, ...props }) => {
  const [field] = useField(props);
  return (
    <>
      {formConfig.access.members_visibility.map((item) => (
        <React.Fragment key={item.value}>
          <RadioField
            key={item.value}
            fieldPath="access.members_visibility"
            label={item.text}
            labelIcon={item.icon}
            checked={_get(field.value, "access.members_visibility") === item.value}
            value={item.value}
          />
          <label className="helptext">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

MembersVisibilityField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

MembersVisibilityField.defaultProps = {
  label: "",
};

const MemberPolicyField = ({ label, formConfig, ...props }) => {
  const [field] = useField(props);
  const isDisabled = _get(field.value, "access.visibility") === "restricted";

  return (
    <>
      {formConfig.access.member_policy.map((item) => (
        <React.Fragment key={item.value}>
          <RadioField
            key={item.value}
            fieldPath="access.member_policy"
            label={item.text}
            labelIcon={item.icon}
            checked={item.value === _get(field.value, "access.member_policy")}
            value={item.value}
            disabled={isDisabled}
          />
          <label className="helptext">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

MemberPolicyField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

MemberPolicyField.defaultProps = {
  label: "",
};

class CommunityPrivilegesForm extends Component {
  getInitialValues = () => {
    return {
      access: {
        visibility: "public",
        members_visibility: "public",
        member_policy: "closed",
      },
    };
  };

  render() {
    const { formConfig, community } = this.props;
    return (
      <CommunitySettingsForm
        initialValues={this.getInitialValues()}
        community={community}
      >
        <Header as="h2" size="small">
          {i18next.t("Community visibility")}
          <Header.Subheader className="mt-5">
            {i18next.t(
              "Controls if the community is visible to anyone or to members only."
            )}
          </Header.Subheader>
        </Header>
        <VisibilityField formConfig={formConfig} />

        <Header as="h2" size="small">
          {i18next.t("Members visibility")}
          <Header.Subheader className="mt-5">
            {i18next.t(
              "Controls if the members tab is visible to anyone or to members only."
            )}
          </Header.Subheader>
        </Header>
        <MembersVisibilityField formConfig={formConfig} />

        {!_isEmpty(formConfig.access.member_policy) && (
          <>
            <Header as="h2" size="small">
              {i18next.t("Membership Policy")}
              <Header.Subheader className="mt-5">
                {i18next.t("Controls if anyone can request to join your community.")}
              </Header.Subheader>
            </Header>
            <MemberPolicyField formConfig={formConfig} />
          </>
        )}
      </CommunitySettingsForm>
    );
  }
}

CommunityPrivilegesForm.propTypes = {
  community: PropTypes.object.isRequired,
  formConfig: PropTypes.object.isRequired,
};

export default CommunityPrivilegesForm;
