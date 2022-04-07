import ActionDropdown from "@js/invenio_communities/members/components/ActionDropdown";
import {
  CommunityMembersApi
} from '@js/invenio_communities/api';
import { SearchResultsRowCheckbox } from "../../components/bulk_actions/SearchResultsRowCheckbox";
import React, { Component } from "react";
import {
  Grid,
  Item,
  Button,
  Label,
  Table,
  Dropdown,
} from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { Image } from "react-invenio-forms";
import PropTypes from "prop-types";
import { DateTime } from "luxon";
import _upperFirst from "lodash/upperFirst";
import { config as mockedConfig } from "../../mockedData";

const timestampToRelativeTime = (timestamp) =>
  DateTime.fromISO(timestamp).setLocale(i18next.language).toRelative();

const dropdownVisibilityOptionsGenerator = (value) => {
  return value.map((element) => {
    return {
      key: element.value,
      text: element.title,
      value: element.value,
      content: (
        <Item.Group>
          <Item className="members-dropdown-option">
            <Item.Content>
              <Item.Description>
                <strong>{element.title}</strong>
              </Item.Description>
              <Item.Meta>{element.description}</Item.Meta>
            </Item.Content>
          </Item>
        </Item.Group>
      ),
    };
  });
};

export class ManagerMemberViewResultItem extends Component {
  constructor(props) {
    super(props);
    const {result} = props;
    this.membersApi = new CommunityMembersApi(result.links);
    this.state = {"result": result};
  }

  updateVisibility = (value) => {
    const visible = value === "public";
    // TODO: membersApi.edit(result); + NOTIFICATIONS
  };

  updateMember = (data) =>{
    const {result} = this.state;
    this.setState({result: { ...result, ...data }})
  }

  render() {
    const { result, config } = this.props;
    const avatar = result.member.links.avatar;
    return (
      <Table.Row>
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item className="flex" key={result.id}>
                <SearchResultsRowCheckbox rowId={result.id} />
                <Image src={avatar} avatar />
                <Item.Content className="ml-10">
                  <Item.Header
                    className={!result.member.description ? "mt-5" : ""}
                  >
                    <a
                      className={result.member.is_group && "mt-10"}
                      href={`/members/${result.id}`}
                    >
                      {result.member.name}
                    </a>
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
            <Dropdown
              selection
              value={result.visible ? "public" : "hidden"} //TODO: Improve this
              options={dropdownVisibilityOptionsGenerator(
                mockedConfig.visibility.options
              )}
              onChange={this.updateVisibility}
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
              successCallback={this.updateMember}
              action={this.invitationsApi.updateRole}
              currentValue={result.role}
            />
          ) : (
            _upperFirst(result.role)
          )}
        </Table.Cell>
        <Table.Cell>
          {result.permissions.can_leave && (
            <Button
              fluid
              negative
              onClick={() => {
                // TODO: implement api call + redirect
              }}
            >
              {i18next.t("Leave...")}
            </Button>
          )}
          {result.permissions.can_delete && (
            <Button
              fluid
              onClick={() => {
                // TODO: implement api call + redirect
              }}
            >
              {i18next.t("Remove...")}
            </Button>
          )}
        </Table.Cell>
      </Table.Row>
    );
  }
}

ManagerMemberViewResultItem.propTypes = {
  result: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
};
