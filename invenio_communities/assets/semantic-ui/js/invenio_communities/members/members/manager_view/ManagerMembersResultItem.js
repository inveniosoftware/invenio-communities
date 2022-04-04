import ActionDropdown from "@js/invenio_communities/members/components/ActionDropdown";
import { MembersContext } from "../../../api/members/MembersContextProvider";
import { SearchResultsRowCheckbox } from "../../components/bulk_actions/SearchResultsRowCheckbox";
import React, { Component } from "react";
import { Grid, Item, Button, Label, Table } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { Image } from "react-invenio-forms";
import PropTypes from "prop-types";
import { DateTime } from "luxon";
import _upperFirst from "lodash/upperFirst";
import { ModalContext } from "../../components/modal_manager";
import { modalModeEnum } from "../../components/RemoveMemberModal";

const timestampToRelativeTime = (timestamp) =>
  DateTime.fromISO(timestamp).setLocale(i18next.language).toRelative();

const dropdownVisibilityOptionsGenerator = (options) => {
  return Object.entries(options).map(([key, settings]) => {
    return {
      key: key,
      text: settings.title,
      value: settings.visible,
      content: (
        <Item.Group>
          <Item className="members-dropdown-option">
            <Item.Content>
              <Item.Description>
                <strong>{settings.title}</strong>
              </Item.Description>
              <Item.Meta>{settings.description}</Item.Meta>
            </Item.Content>
          </Item>
        </Item.Group>
      ),
    };
  });
};

export class ManagerMembersResultItem extends Component {
  static contextType = MembersContext;

  constructor(props) {
    super(props);
    const { result } = props;
    this.state = { result: result };
  }

  updateMemberRole = (data, value) => {
    const { result } = this.state;
    this.setState({ result: { ...result, ...{ role: value } } });
  };

  updateMemberVisibility = (data, value) => {
    const { result } = this.state;
    this.setState({ result: { ...result, ...{ visible: value } } });
  };

  openLeaveOrRemoveModal = (openModalCallback, isRemoving = true) => {
    const { result } = this.props;
    const { api } = this.context;

    const { member } = result;

    const modalAction = () => api.removeMember(member);
    const modalMode = isRemoving ? modalModeEnum.remove : modalModeEnum.leave;

    openModalCallback({ modalMode, modalAction });
  };

  render() {
    const { config } = this.props;
    const { result } = this.state;
    const { api } = this.context;

    const avatar = result.member.links.avatar;
    return (
      <Table.Row>
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item className="flex" key={result.id}>
                <SearchResultsRowCheckbox rowId={result.id} data={result} />
                <Image src={avatar} avatar />
                <Item.Content className="ml-10">
                  <Item.Header
                    className={!result.member.description ? "mt-5" : ""}
                  >
                    <b>{result.member.name}</b>

                    {result.member.is_group && (
                      <Label className="ml-10">{i18next.t("Group")}</Label>
                    )}
                    {result.is_current_user && (
                      <Label color="blue" className="ml-10">
                        {i18next.t("You")}
                      </Label>
                    )}
                  </Item.Header>
                  {result.member.description && (
                    <Item.Meta>
                      <div
                        className="truncate-lines-1"
                        dangerouslySetInnerHTML={{
                          __html: result.member.description,
                        }}
                      />
                    </Item.Meta>
                  )}
                </Item.Content>
              </Item>
            </Grid.Column>
          </Grid>
        </Table.Cell>
        <Table.Cell>{timestampToRelativeTime(result.created)}</Table.Cell>
        <Table.Cell>
          {result.permissions.can_update_visible ? (
            <ActionDropdown
              options={config.visibility}
              successCallback={this.updateMemberVisibility}
              action={api.updateVisibility}
              currentValue={result.visible}
              resource={result}
              optionsSerializer={dropdownVisibilityOptionsGenerator}
            />
          ) : result.visible ? (
            "Public"
          ) : (
            "Hidden"
          )}
        </Table.Cell>
        <Table.Cell>
          {result.permissions.can_update_role ? (
            <ActionDropdown
              options={config.roles}
              successCallback={this.updateMemberRole}
              action={api.updateRole}
              currentValue={result.role}
              resource={result}
            />
          ) : (
            _upperFirst(result.role)
          )}
        </Table.Cell>

        <ModalContext.Consumer>
          {({ openModal }) => (
            <Table.Cell>
              {result.permissions.can_leave && (
                <Button
                  fluid
                  negative
                  onClick={() => this.openLeaveOrRemoveModal(openModal, false)}
                >
                  {i18next.t("Leave...")}
                </Button>
              )}
              {result.permissions.can_delete && (
                <Button
                  fluid
                  onClick={() => this.openLeaveOrRemoveModal(openModal, true)}
                >
                  {i18next.t("Remove...")}
                </Button>
              )}
            </Table.Cell>
          )}
        </ModalContext.Consumer>
      </Table.Row>
    );
  }
}

ManagerMembersResultItem.propTypes = {
  result: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
};
