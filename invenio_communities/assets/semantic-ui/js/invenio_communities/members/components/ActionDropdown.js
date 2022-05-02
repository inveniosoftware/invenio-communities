import { errorSerializer } from "../../api/serializers";
import { ErrorPopup } from "./ErrorPopup";
import { SuccessIcon } from "./SuccessIcon";
import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { Dropdown, List } from "semantic-ui-react";
import { withCancel } from "react-invenio-forms";

const dropdownOptionsGenerator = (value) => {
  return value.map((settings) => {
    return {
      key: settings.key,
      text: settings.title,
      value: settings.key,
      content: (
        <List>
          <List.Item>
            <List.Content>
              <List.Header>{settings.title}</List.Header>
              <List.Description>{settings.description}</List.Description>
            </List.Content>
          </List.Item>
        </List>
      ),
    };
  });
};

class ActionDropdown extends Component {
  constructor(props) {
    super(props);
    this.state = { error: undefined, loading: false, actionSuccess: undefined };
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  handleOnChange = async (e, { value }) => {
    const { successCallback, action, resource } = this.props;
    this.setState({ loading: true, actionSuccess: false });
    this.cancellableAction = withCancel(action(resource.member, value));

    try {
      const response = await this.cancellableAction.promise;
      successCallback(response, value);
      this.setState({ loading: false, actionSuccess: true });
    } catch (error) {
      if (error === "UNMOUNTED") return;
      this.setState({ error: errorSerializer(error), loading: false });
    }
  };

  render() {
    const { loading, actionSuccess, error } = this.state;
    const { options, currentValue, optionsSerializer, disabled } = this.props;

    return (
      <Overridable
        id="InvenioCommunities.ActionDropdown.layout"
        options={options}
        loading={loading}
        actionSuccess={actionSuccess}
        error={error}
        disabled={disabled}
        optionsSerializer={optionsSerializer}
      >
        <>
          <Dropdown
            options={optionsSerializer(options)}
            selection
            loading={loading}
            value={currentValue}
            openOnFocus={false}
            selectOnBlur={false}
            onChange={this.handleOnChange}
            className="mr-10"
            disabled={disabled}
          />
          {actionSuccess && (
            <SuccessIcon timeOutDelay={4000} show={actionSuccess} />
          )}
          {error && <ErrorPopup error={error} />}
        </>
      </Overridable>
    );
  }
}

ActionDropdown.propTypes = {
  options: PropTypes.object.isRequired,
  successCallback: PropTypes.func.isRequired,
  currentValue: PropTypes.oneOfType([PropTypes.string, PropTypes.bool]),
  action: PropTypes.func.isRequired,
  optionsSerializer: PropTypes.func,
  disabled: PropTypes.bool,
  resource: PropTypes.object.isRequired,
};

ActionDropdown.defaultProps = {
  currentValue: "",
  disabled: false,
  optionsSerializer: dropdownOptionsGenerator,
};

export default Overridable.component("ActionDropdown", ActionDropdown);
