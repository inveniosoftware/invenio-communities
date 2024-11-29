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
                href={organizations[0].url}
                aria-label={`${organizations[0].name}'s ${organizations[0].label} profile`}
                title={`${organizations[0].name}'s ${organizations[0].label} profile`}
                target="_blank"
                rel="noreferrer"
              >
                {organizations[0].name}
                <span>&nbsp;</span>
                <img
                  className="inline-id-icon"
                  src={organizations[0].icon}
                  alt={`${organizations[0].name}'s ${organizations[0].label} profile`}
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
                            href={org.url}
                            aria-label={`${org.name}'s ${org.label} profile`}
                            title={`${org.name}'s ${org.label} profile`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {org.name}
                            <span>&nbsp;</span>
                            <img
                              className="inline-id-icon"
                              src={org.icon}
                              alt={`${org.name}'s ${org.label} profile`}
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
      label: PropTypes.string,
      icon: PropTypes.string,
      url: PropTypes.string,
    })
  ).isRequired,
};

export default OrganizationsList;
