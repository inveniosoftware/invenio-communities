import {
  errorSerializer
} from '@js/invenio_communities/api/config';
import { ErrorPopup } from "./ErrorPopup";
import { SuccessIcon } from "./SuccessIcon";
import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { Dropdown, List } from "semantic-ui-react";

const dropdownOptionsGenerator = (value) => {
  return Object.entries(value).map(([key, settings]) => {
    return {
      key: key,
      text: settings.title,
      value: key,
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

  handleOnChange = async (e, { value, id }) => {
    const { successCallback, action } = this.props;
    this.setState({ loading: true, actionSuccess: false });
    try {
      const response = await action(value, id);
      successCallback(response);
      this.setState({ loading: false, actionSuccess: true });
    } catch (error) {
      this.setState({ error: errorSerializer(error), loading: false });
    }
  };

  render() {
    const { loading, actionSuccess, error } = this.state;
    const { options, currentValue } = this.props;
    return (
      <Overridable
        id="InvenioCommunities.ActionDropdown.layout"
        options={options}
        loading={loading}
        actionSuccess={actionSuccess}
        error={error}
      >
        <>
          <Dropdown
            options={dropdownOptionsGenerator(options)}
            selection
            loading={loading}
            value={currentValue}
            openOnFocus={false}
            selectOnBlur={false}
            onChange={this.handleOnChange}
            className="mr-10"
          />
          {actionSuccess && <SuccessIcon timeOutDelay={4000}
                                         success={actionSuccess}/>}
          {error && <ErrorPopup error={error} />}
        </>
      </Overridable>
    );
  }
}

ActionDropdown.propTypes = {
  options: PropTypes.object.isRequired,
  successCallback: PropTypes.func.isRequired,
  currentValue: PropTypes.string,
  action: PropTypes.func.isRequired,
};

ActionDropdown.defaultProps = {
  currentValue: "",
};

export default Overridable.component("ActionDropdown", ActionDropdown);
