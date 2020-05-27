import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import axios from "axios";

import "semantic-ui-css/semantic.min.css";
import {
  Accordion,
  Image,
  Divider,
  Input,
  Icon,
  List,
  Form,
  Message,
  TextArea,
  Button,
  Dropdown,
} from "semantic-ui-react";

const useInvenioSearchAPI = (baseURL) => {
  const [query, setQuery] = useState("");
  const [data, setData] = useState({ hits: { total: 0, hits: [] } });
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsError(false);
      setIsLoading(true);
      try {
        const result = await axios(`${baseURL}?q=${query}`);
        setData(result.data);
      } catch (error) {
        setIsError(true);
      }
      setIsLoading(false);
    };
    fetchData();
  }, [query]);
  return [{ query, data, isLoading, isError }, setQuery];
};

const CommunitiesRequestDropdown = () => {
  const [community, setCommunity] = useState(null);
  const [message, setMessage] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const toggleOpen = () => setIsOpen(!isOpen);
  const [response, setResponse] = useState(null);
  const [{ query, data, isLoading, isError }, setQuery] = useInvenioSearchAPI(
    "/api/communities"
  );

  const handleSubmit = () => {
    axios
      .post(`/api/communities/${community.metadata.id}/requests/inclusion`, {
        record_pid: __RECORD.recid,
        message: message,
      })
      .then((resp) => {
        console.log(resp.data);
        setResponse({
          data: resp.data,
          message: (
            <>
              Request to{" "}
              <a href={`/communities/${community.metadata.id}`}>
                {community.metadata.title}
              </a>{" "}
              submitted
            </>
          ),
          status: "success",
        });
      })
      .catch((error) => {
        console.log(error.response);
        setResponse({
          response: error.response,
          message:
            error.response.status == 500
              ? "Unknown error"
              : error.response.data.message,
          status: "error",
        });
      })
      .finally(() => {
        setCommunity(null);
        setMessage("");
        toggleOpen();
      });
  };

  const handleCancel = () => {
    setCommunity(null);
    setMessage("");
    setResponse(null);
    toggleOpen();
  };

  const options = data.hits.hits.map((community) => ({
    key: community.metadata.id,
    text: community.metadata.title,
    value: community,
  }));
  return (
    <>
      <Dropdown
        text="Add community"
        icon="add"
        labeled
        button
        className="icon"
        open={isOpen}
        onClose={handleCancel}
        onClick={toggleOpen}
      >
        <Dropdown.Menu onClick={(e) => e.stopPropagation()}>
          {community ? (
            <Dropdown.Item selected={false} active={false}>
              <Form>
                <p>
                  Request for this record to be added to{" "}
                  <a href={`/communities/${community.metadata.id}`}>
                    {community.metadata.title}
                  </a>
                </p>
                <Form.Input
                  label="Message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Write a message for the community curator..."
                />
                <Button positive onClick={handleSubmit}>
                  Submit
                </Button>
                <Button negative onClick={handleCancel}>
                  Cancel
                </Button>
              </Form>
            </Dropdown.Item>
          ) : (
            <>
              <Dropdown.Header content="Search communities" />
              <Input
                icon="search"
                value={query}
                // TODO: debounce
                onChange={(e) => setQuery(e.target.value)}
                iconPosition="left"
                name="community-query"
              />
              {options.map(({ key, text, value }) => (
                <Dropdown.Item
                  key={key}
                  text={text}
                  onClick={() => setCommunity(value)}
                />
              ))}
            </>
          )}
        </Dropdown.Menu>
      </Dropdown>
      {/* TODO: extract error message into separate component */}
      {response ? (
        <Message
          size="tiny"
          positive={response.status !== "error"}
          negative={response.status === "error"}
        >
          {response.message}
        </Message>
      ) : null}
    </>
  );
};

const CommunityItem = ({ community }) => (
  <List.Item>
    {/* TODO: Add logos */}
    {/* <Image src={community.logo} avatar size="tiny" /> */}
    <List.Header as="a" href={`/communities/${community.comid}`}>
      {community.title}
    </List.Header>
  </List.Item>
);

const CommunityPendingItem = ({ community }) => {
  const [response, setResponse] = useState(null);

  const handle = (action) => {
    return () => {
      axios
        .post(
          `/api/communities/${community.comid}/requests/inclusion/${community.request_id}/${action}`
        )
        .then((resp) => {
          console.log(resp.data);
          setResponse({
            response: resp,
            message: `Request ${action}ed`,
            status: "success",
          });
        })
        .catch((error) => {
          console.log(error.response);
          setResponse({
            response: error.response,
            message:
              error.response.status == 500
                ? "Unknown error"
                : error.response.data.message,
            status: "error",
          });
        });
    };
  };

  return (
    <List.Item>
      <List.Content>
        <List.Header as="a" href={`/communities/${community.comid}`}>
          {community.title}
        </List.Header>
        <Icon link onClick={handle("accept")} color="green" name="check" />
        <Icon link onClick={handle("reject")} color="red" name="x" />
        <Icon link onClick={handle("comment")} name="comment" />
        {response ? (
          <List.Description>
            <Message
              size="tiny"
              positive={response.status !== "error"}
              negative={response.status === "error"}
            >
              {response.message}
            </Message>
          </List.Description>
        ) : null}
      </List.Content>
    </List.Item>
  );
};

const CommunityGallery = ({ communities, renderItem }) => {
  const RenderItem = renderItem || CommunityItem;
  return (
    <List>
      {communities.map((community) => (
        <RenderItem key={community.id} community={community} />
      ))}
    </List>
  );
};

const App = () => {
  const accepted_communities = __RECORD_COMMUNITIES.accepted || [];
  const pending_communities = __RECORD_COMMUNITIES.pending || [];

  return (
    <>
      <CommunityGallery communities={accepted_communities} />
      <Accordion
        panels={[
          {
            key: "pending-requests",
            title: `Pending requests (${pending_communities.length})`,
            content: {
              content: (
                <>
                  <CommunityGallery
                    renderItem={CommunityPendingItem}
                    communities={pending_communities}
                  />
                </>
              ),
            },
          },
        ]}
      />
      <Divider />
      <CommunitiesRequestDropdown />
    </>
  );
};

const domContainer = document.querySelector("#communities-management");
const __RECORD = JSON.parse(domContainer.dataset.record);
const __RECORD_COMMUNITIES = JSON.parse(domContainer.dataset.communities);
ReactDOM.render(<App />, domContainer);
