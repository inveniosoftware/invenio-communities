import React from "react";
import {
  SearchAppFacets,
  SearchAppResultsPane,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { SearchBar } from "react-searchkit";
import { Button, Container, Grid } from "semantic-ui-react";
import PropTypes from "prop-types";

export const CommunitiesSearchLayout = ({ config, appName }) => {
  const [sidebarVisible, setSidebarVisible] = React.useState(false);
  return (
    <Container>
      <Grid>
        <Grid.Row>
          <Grid.Column
            only="mobile tablet"
            mobile={2}
            tablet={1}
            verticalAlign="middle"
            className="mt-10"
          >
            <Button
              basic
              icon="sliders"
              onClick={() => setSidebarVisible(true)}
              aria-label={i18next.t("Filter results")}
            />
          </Grid.Column>
          <Grid.Column
            mobile={14}
            tablet={9}
            computer={8}
            floated="right"
            className="mt-10"
          >
            <SearchBar placeholder={i18next.t("Search communities...")} />
          </Grid.Column>
          <Grid.Column mobile={16} tablet={6} computer={4} className="mt-10">
            <Button
              positive
              icon="upload"
              labelPosition="left"
              href="/communities/new"
              content={i18next.t("New community")}
              floated="right"
            />
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <GridResponsiveSidebarColumn
            width={4}
            open={sidebarVisible}
            onHideClick={() => setSidebarVisible(false)}
            // eslint-disable-next-line react/no-children-prop
            children={<SearchAppFacets aggs={config.aggs} appName={appName} />}
          />
          <Grid.Column mobile={16} tablet={16} computer={12}>
            <SearchAppResultsPane
              layoutOptions={config.layoutOptions}
              appName={appName}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Container>
  );
};

CommunitiesSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.object.isRequired,
};
