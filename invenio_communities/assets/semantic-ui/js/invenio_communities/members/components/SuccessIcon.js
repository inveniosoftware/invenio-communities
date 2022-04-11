import React, { Component } from "react";
import PropTypes from "prop-types";
import { Icon } from "semantic-ui-react";

export class SuccessIcon extends Component {
  constructor(props) {
    super(props);
    const { show } = props;
    this.state = { show: show };
  }

  componentDidMount() {
    const { timeOutDelay, show } = this.props;
    this.setState({ show: show });

    const timerAlreadySet = !!this.successTimer;

    if (show) {
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
    this.setState({ show: false });
  };

  render() {
    const { show } = this.state;
    return show && <Icon color="green" name="checkmark" />;
  }
}

SuccessIcon.propTypes = {
  timeOutDelay: PropTypes.number.isRequired,
  show: PropTypes.bool,
};

SuccessIcon.defaultProps = {
  show: false,
};
