import React, { Component } from "react";
import PropTypes from "prop-types";
import { Message } from "semantic-ui-react";
import { ErrorMessage as FormikError } from "formik";

export class ErrorMessage extends Component {
  renderFormField = (message) => {
    return message ? <Message negative content={message}></Message> : null;
  };

  render() {
    const { fieldPath } = this.props;
    return <FormikError name={fieldPath}>{this.renderFormField}</FormikError>;
  }
}

ErrorMessage.propTypes = {
  fieldPath: PropTypes.string.isRequired,
};
