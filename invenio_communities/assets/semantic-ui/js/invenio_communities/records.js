import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import _isEmpty from 'lodash/isEmpty';

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
      .post(`/api/communities/${community.metadata.id}/records/requests`, {
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

const CommunityItem = ({ communityRecord }) => (
  <List.Item>
    {/* TODO: Add logos */}
    {/* <Image src={communityRecord.logo} avatar size="tiny" /> */}
    <List.Header as="a" href={`/communities/${communityRecord.comid}`}>
      {communityRecord.community_title}
    </List.Header>
    <CommunitiesCollectionDropdown communityRecord={communityRecord} />
  </List.Item>
);

const CommunityPendingItem = ({ communityRecord }) => {
  const [response, setResponse] = useState(null);
  const [showMessageInput, setShowMessageInput] = useState(false);
  const [message, setMessage] = useState("");
  debugger
  const handle = (action) => {
    return () => {
      axios
        .post(
          `/api/communities/${communityRecord.comid}/records/requests/${communityRecord.id}/${action}`,
          { 'message': message }
        )
        .then((resp) => {
          if (action == 'comment') {
            setShowMessageInput(false);
          }
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
    <>
      <List.Item>
        <List.Content>
          <List.Header as="a" href={`/communities/${communityRecord.comid}`}>
            {communityRecord.community_title}
          </List.Header>
          <Icon link onClick={handle("accept")} color="green" name="check" />
          <Icon link onClick={handle("reject")} color="red" name="x" />
          <Icon link onClick={() => setShowMessageInput(true)} name="comment" />
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
      {showMessageInput ?
        <div className="ui active modal">
          <Form>
            <div className="content">
              <p>
                Send a message to the other party.
          </p>
              <Form.Input
                label="Message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Write a message for the community curator..."
              />
            </div>
            <div className="actions">
              <Button positive onClick={handle("comment")}>
                Submit
          </Button>
              <Button negative onClick={() => setShowMessageInput(false)}>
                Cancel
          </Button>
            </div>
          </Form>
        </div> : null}
    </>
  );
};

const CommunityGallery = ({ communitiesRecords, renderItem }) => {
  const RenderItem = renderItem || CommunityItem;
  return (
    <List>
      {communitiesRecords.map((communityRecord) => (
        <RenderItem key={communityRecord.id} communityRecord={communityRecord} />
      ))}
    </List>
  );
};

const App = () => {
  const accepted_communities = __RECORD_COMMUNITIES.accepted || [];
  const pending_communities = __RECORD_COMMUNITIES.pending || [];
  return (
    <>
      <CommunityGallery communitiesRecords={accepted_communities} />
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
                    communitiesRecords={pending_communities}
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

const CommunitiesCollectionDropdown = ({ communityRecord }) => {
  const [ongoingRequest, setOngoingRequest] = useState(false);
  const [response, setResponse] = useState(null);
  const [toggleEdit, setToggleEdit] = useState(false);
  const recordCollections= communityRecord._collections || []
  const [currentCollections, setCurrentCollections] = useState(recordCollections.map((collection)=>
  collection.id
));


  const handleChange = (new_collections) => {
    setOngoingRequest(true);
    axios
      .put(`/api/communities/${communityRecord.comid}/records/${__RECORD.recid}`, {
        'collections': new_collections.map(collection => ({
          'id': collection
        }))
      })
      .then((resp) => {
        setCurrentCollections(new_collections);
        setResponse({
          // TODO
          data: resp.data,
          message: (
            <>
              The collections for this record have been updated.
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
        setOngoingRequest(false);
      });
  };

  const availableCollections = __COMMUNITIES[communityRecord.comid]._collections || {}

  const options = Object.entries(availableCollections).map(([collection_id, collection]) => ({
    key: collection_id,
    text: collection.title,
    value: collection_id,
  }));


console.log(availableCollections)
  return (
    (!_isEmpty(options) ?
      ( toggleEdit ? (
      <>
      <Dropdown
        placeholder='collections'
        fluid
        multiple selection
        disabled={ongoingRequest}
        options={options}
        defaultValue={currentCollections}
        onChange={(e, { value }) => handleChange(value)} />
        { response ? (
            <Message
              size="tiny"
              positive={response.status !== "error"}
              negative={response.status === "error"}
            >
              {response.message}
            </Message>
          ) : null
        }
        <Button positive size="small" onClick={() => setToggleEdit(false)}>Done</Button>
      </>):
      <>
      <List>
        {currentCollections.map((collection_id)=>(
          <List.Item key={collection_id}>
            <List.Header>
              {availableCollections[collection_id].title}
            </List.Header>
          </List.Item>
        ))}
      </List>
      <Button color="orange" size="small" onClick={() => setToggleEdit(true)}>Edit</Button>
      </>
      )
      : null)
  );
};


const domContainer = document.querySelector("#communities-management");
const __RECORD = JSON.parse(domContainer.dataset.record);
const __COMMUNITIES_DATA = JSON.parse(domContainer.dataset.communities)
const __RECORD_COMMUNITIES = __COMMUNITIES_DATA.record_communities;
const __COMMUNITIES = __COMMUNITIES_DATA.communities;

ReactDOM.render(<App />, domContainer);
