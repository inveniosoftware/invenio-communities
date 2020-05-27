import React, { Component } from "react";
import PropTypes from "prop-types";
import { FastField, Field, getIn } from "formik";
import { Form } from "semantic-ui-react";

import { ErrorMessage } from "./ErrorMessage";

export class TextField extends Component {
  renderFormField = (props) => {
    const { fieldPath, optimized, ...uiProps } = this.props;
    const {
      form: { values, handleChange, handleBlur },
    } = props;
    const FormComponent =
      this.props.as === "input" ? Form.Input : Form.TextArea;

    return (
      <Form.Field id={fieldPath}>
        <FormComponent
          id={fieldPath}
          name={fieldPath}
          onChange={handleChange}
          onBlur={handleBlur}
          value={getIn(values, fieldPath, "")}
          {...uiProps}
        ></FormComponent>
        <ErrorMessage fieldPath={fieldPath} />
      </Form.Field>
    );
  };

  render() {
    const FormikField = this.props.optimized ? FastField : Field;

    return (
      <FormikField
        name={this.props.fieldPath}
        component={this.renderFormField}
      />
    );
  }
}

TextField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  optimized: PropTypes.bool,
  as: PropTypes.oneOf(["input", "textarea"]),
};

TextField.defaultProps = {
  optimized: false,
  as: "input",
};
