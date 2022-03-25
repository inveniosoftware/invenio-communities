import React, { Component } from "react";
import PropTypes from "prop-types";
import { Icon } from "semantic-ui-react";

export class SuccessIcon extends Component {
  constructor(props) {
    super(props);
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    const { timeOutDelay, onTimeOut, success } = this.props;

    const timerAlreadySet = !!this.successTimer;

    if (success) {
      if (timerAlreadySet) {
        clearTimeout(this.successTimer);
      }

      this.successTimer = setTimeout(onTimeOut, timeOutDelay);
    }
  }

  componentWillUnmount() {
    this.successTimer && clearTimeout(this.successTimer);
  }

  render() {
    const { success } = this.props;

    return success ? <Icon color="green" name="checkmark" /> : null;
  }
}

SuccessIcon.propTypes = {
  timeOutDelay: PropTypes.number.isRequired,
  onTimeOut: PropTypes.func.isRequired,
  success: PropTypes.bool.isRequired,
};
