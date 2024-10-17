import React from "react";
import PropTypes from "prop-types";
import { Popup } from "semantic-ui-react";

const OrganizationsList = ({ organizations }) => {
  const handleClick = (e) => {
    e.preventDefault();
  };

  return (
    <div>
      {organizations && organizations.length > 0 && (
        <div>
          <span className="org-list-inline">
            <i className="building outline icon" aria-hidden="true" />
            {organizations[0].id ? (
              <a
                href={`https://ror.org/${organizations[0].id}`}
                aria-label={`${organizations[0].name}'s ROR profile`}
                title={`${organizations[0].name}'s ROR profile`}
                target="_blank"
                rel="noreferrer"
              >
                {organizations[0].name}
                <span>&nbsp;</span>
                <img
                  className="inline-id-icon"
                  src="/static/images/ror-icon.svg"
                  alt={`${organizations[0].name}'s ROR profile`}
                />
              </a>
            ) : (
              organizations[0].name
            )}
          </span>
          {organizations.length > 1 && (
            <span className="ml-1">
              &nbsp;and&nbsp;
              <Popup
                trigger={
                  <a href="#!" onClick={handleClick}>
                    {`${organizations.length - 1} more organizations`}
                  </a>
                }
                size="small"
                wide="very"
                content={
                  <div className="expanded-orgs">
                    {organizations.slice(1).map((org, index) => (
                      <div key={org.id || org.name} className="inline-computer mt-5">
                        {org.id ? (
                          <a
                            href={`https://ror.org/${org.id}`}
                            aria-label={`${org.name}'s ROR profile`}
                            title={`${org.name}'s ROR profile`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {org.name}
                            <span>&nbsp;</span>
                            <img
                              className="inline-id-icon"
                              src="/static/images/ror-icon.svg"
                              alt={`${organizations[0].name}'s ROR profile`}
                            />
                          </a>
                        ) : (
                          org.name
                        )}
                        {index < organizations.length - 2 && <span>{", "}&nbsp;</span>}
                      </div>
                    ))}
                  </div>
                }
                on="click"
                position="bottom left"
                positionFixed
              />
            </span>
          )}
        </div>
      )}
    </div>
  );
};

OrganizationsList.propTypes = {
  organizations: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string.isRequired,
    })
  ).isRequired,
};

export default OrganizationsList;
