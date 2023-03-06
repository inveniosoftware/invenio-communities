import { InvenioSearchPagination } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import { Count, ResultsList, Sort } from "react-searchkit";
import { Grid, Segment } from "semantic-ui-react";
import PropTypes from "prop-types";

export const CommunitiesResults = ({
  sortOptions,
  paginationOptions,
  currentResultsState,
}) => {
  const { total } = currentResultsState.data;
  return (
    total && (
      <Grid>
        <Grid.Row>
          <Grid.Column width={16}>
            <Segment>
              <Grid>
                <Grid.Row
                  verticalAlign="middle"
                  className="small pt-5 pb-5 highlight-background"
                >
                  <Grid.Column width={4}>
                    <Count
                      label={() => (
                        <>
                          {i18next.t("{{total}} result(s) found", {
                            total: total,
                          })}
                        </>
                      )}
                    />
                  </Grid.Column>
                  <Grid.Column width={12} textAlign="right" className="pr-5">
                    {sortOptions && (
                      <Sort
                        values={sortOptions}
                        label={(cmp) => (
                          <>
                            <label className="mr-10">{i18next.t("Sort by")}</label>
                            {cmp}
                          </>
                        )}
                      />
                    )}
                  </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                  <Grid.Column>
                    <ResultsList />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <InvenioSearchPagination paginationOptions={paginationOptions} />
      </Grid>
    )
  );
};

CommunitiesResults.propTypes = {
  paginationOptions: PropTypes.object.isRequired,
  sortOptions: PropTypes.object.isRequired,
  currentResultsState: PropTypes.object.isRequired,
};
