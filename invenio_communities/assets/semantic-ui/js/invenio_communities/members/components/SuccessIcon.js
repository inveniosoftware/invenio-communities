import React, { Component } from "react";
import PropTypes from "prop-types";
import { Icon } from "semantic-ui-react";

export class SuccessIcon extends Component {
  constructor(props) {
    super(props);
    const { success } = props;
    this.state = { "success": success };
  }

  componentDidMount() {
    const { timeOutDelay, success } = this.props;
    this.setState({ success: success });

    const timerAlreadySet = !!this.successTimer;

    if (success) {
      if (timerAlreadySet) {
        clearTimeout(this.successTimer);
      }

      this.successTimer = setTimeout(this.handleOnTimeOut, timeOutDelay);
    }
  }

  componentWillUnmount() {
    this.successTimer && clearTimeout(this.successTimer);
  }

  handleOnTimeOut = () => {
    this.setState({ success: false });
  };

  render() {
    const { success } = this.state;
    return success && <Icon color="green" name="checkmark" />;
  }
}

SuccessIcon.propTypes = {
  timeOutDelay: PropTypes.number.isRequired,
  success: PropTypes.bool,
};

SuccessIcon.defaultProps = {
  success: false,
};
