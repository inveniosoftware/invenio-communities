import React, { Component } from "react";
import { Grid, Item, Button, Label, Table } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { i18next } from "@translations/invenio_communities/i18next";
import { Image } from "react-invenio-forms";
import PropTypes from "prop-types";
import { MemberDropdown } from "../components/Dropdowns";
import { config, isMember } from "../mockedData";
import { DateTime } from "luxon";

const timestampToRelativeTime = (timestamp) =>
  DateTime.fromISO(timestamp).setLocale(i18next.language).toRelative();

const dropdownOptionsGenerator = (value) => {
  return value.map((element) => {
    return {
      key: element.value,
      text: element.title,
      value: element.value,
      content: (
        <Item.Group>
          <Item className="members-dopdown-option">
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

class MemberPublicViewResultItem extends Component {
  render() {
    const { result } = this.props;
    //TODO: remove this check when backend implemented
    const avatar = result.links.avatar
      ? result.links.avatar
      : "/static/images/square-placeholder.png";
    return (
      <Table.Row>
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item className="flex-container" key={result.id}>
                <Image
                  src={avatar}
                  avatar
                  fallbackSrc="/static/images/square-placeholder.png"
                />
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
      </Table.Row>
    );
  }
}

MemberPublicViewResultItem.propTypes = {
  result: PropTypes.object.isRequired,
};

class MemberViewResultItem extends Component {
  updateVisibility = (value) => {
    const { result } = this.props;
    result.visibility = value;
    // TODO: membersApi.edit(result); + NOTIFICATIONS
  };

  updateRole = (value) => {
    const { result } = this.props;
    result.role = value;
    // TODO: membersApi.edit(result); + NOTIFICATIONS
  };

  render() {
    const { result } = this.props;
    //TODO: remove this check when backend implemented
    const avatar = result.links.avatar
      ? result.links.avatar
      : "/static/images/square-placeholder.png";
    return (
      <Table.Row>
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item className="flex-container" key={result.id}>
                <Image
                  src={avatar}
                  avatar
                  fallbackSrc="/static/images/square-placeholder.png"
                />
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
          <MemberDropdown
            initialValue={result.visibility}
            options={dropdownOptionsGenerator(config.visibility.options)}
            updateMember={this.updateVisibility}
          />
        </Table.Cell>
        <Table.Cell>
          <MemberDropdown
            initialValue={result.role}
            options={dropdownOptionsGenerator(config.role.options)}
            updateMember={this.updateRole}
          />
        </Table.Cell>
        <Table.Cell>
          {result.is_current_user && (
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
        </Table.Cell>
      </Table.Row>
    );
  }
}

MemberViewResultItem.propTypes = {
  result: PropTypes.object.isRequired,
};

export function MembersResultsItem({ result, index }) {
  return isMember ? (
    <MemberViewResultItem result={result} />
  ) : (
    <MemberPublicViewResultItem result={result} />
  );
}
