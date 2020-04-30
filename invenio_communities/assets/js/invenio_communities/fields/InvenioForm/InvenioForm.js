import React, { Component } from "react";
import PropTypes from "prop-types";
import { Formik } from "formik";
import { Form, Button, Container } from "semantic-ui-react";

export class InvenioForm extends Component {
  onSubmit = (values, actions) => {
    try {
      actions.setSubmitting(true);
      const response = this.props.onSubmit(values);
      if (this.props.successCallback) {
        this.props.successCallback(response);
      }
    } catch (error) {
      const errors = this.props.onError(error);
      actions.setErrors(errors);
    }
    actions.setSubmitting(false);
  };

  render() {
    const { formik } = this.props;
    return (
      <Container>
        <Formik onSubmit={this.onSubmit} {...formik}>
          {({ isSubmitting, handleSubmit }) => (
            <Form loading={isSubmitting} onSubmit={handleSubmit}>
              {this.props.children}
              <Button
                primary
                disabled={isSubmitting}
                name="submit"
                type="submit"
                content="Submit"
              />
            </Form>
          )}
        </Formik>
      </Container>
    );
  }
}

InvenioForm.propTypes = {
  successCallback: PropTypes.func,
  submitSerializer: PropTypes.func,
  formik: PropTypes.shape({
    initialValues: PropTypes.object.isRequired,
    validationSchema: PropTypes.object,
    validate: PropTypes.func,
  }),
};
