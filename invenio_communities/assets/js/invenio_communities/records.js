import React, { useState, useEffect, useContext } from "react";
import ReactDOM from "react-dom";
import axios from "axios";

import "semantic-ui-css/semantic.min.css";
import {
  Accordion,
  Image,
  Icon,
  Form,
  TextArea,
  Button,
  Dropdown,
  Modal,
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

const CommunitiesSearchDropdown = ({ onSelect }) => {
  const [{ query, data, isLoading, isError }, setQuery] = useInvenioSearchAPI(
    "/api/communities"
  );

  const handleChange = (e, { searchQuery, value }) => {
    setQuery(searchQuery);
    onSelect(value);
  };
  const handleSearchChange = (e, { searchQuery }) => setQuery(searchQuery);

  return (
    <Dropdown
      fluid
      onChange={handleChange}
      onSearchChange={handleSearchChange}
      options={data.hits.hits.map((community) => ({
        key: community.metadata.id,
        text: community.metadata.title,
        value: community,
      }))}
      placeholder="Search communities..."
      search
      searchQuery={query}
      selection
      value=""
    />
  );
};

const CommunityRequestModal = () => {
  const [open, setOpen] = useState(false);
  const [community, setCommunity] = useState(null);
  const [message, setMessage] = useState("");
  const handleSelect = (community) => {
    setCommunity(community);
  };
  const handleSubmit = () => {
    const postData = async () => {
      try {
        const result = await axios.post(
          `/api/communities/${community.metadata.id}/requests/inclusion`,
          {
            record_pid: __RECORD.recid,
            message: message,
          }
        );
        console.log(result.data);
        setOpen(false);
        setCommunity(null);
        setMessage("");
      } catch (error) {
        console.log(error);
      }
    };
    postData();
  };
  return (
    <Modal
      size="small"
      trigger={
        <Button onClick={() => setOpen(true)} icon>
          <Icon name="plus" />
        </Button>
      }
      closeIcon={true}
      open={open}
      onClose={() => setOpen(false)}
    >
      <Modal.Header>Select a community</Modal.Header>
      <Modal.Content image>
        <Modal.Description>
          <CommunitiesSearchDropdown onSelect={handleSelect} />
          {community ? (
            <Form>
              <p>
                Request for this record to be added to "
                {community.metadata.title}"
              </p>
              <Form.Field>
                <label>Message</label>
                <TextArea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Write a message for the community curator..."
                />
              </Form.Field>
              <Button onClick={handleSubmit} type="submit">
                Send request
              </Button>
            </Form>
          ) : null}
        </Modal.Description>
      </Modal.Content>
    </Modal>
  );
};

const CommunityItem = ({ community }) => (
  <>
    {/* TODO: Add logos */}
    {/* <Image src={community.logo} avatar size="tiny" /> */}
    <span>{community.title}</span>
  </>
);

const CommunityPendingItem = ({ community }) => {
  const [message, setMessage] = useState("");

  const handle = (action) => {
    return () => {
      const postData = async () => {
        try {
          const result = await axios.post(
            `/api/communities/${community.id}/requests/inclusion/${community.request_id}/${action}`,
            { message },
          );
          console.log(result.data);
          setMessage("");
        } catch (error) {
          console.log(error);
        }
      };
      postData();
    };
  };

  return (
    <>
      <CommunityItem community={community} />
      <Icon link onClick={handle("accept")} color="green" name="check" />
      <Icon link onClick={handle("reject")} color="red" name="x" />
      <Icon link onClick={handle("comment")} name="comment" />
    </>
  );
};

const CommunityGallery = ({ communities, renderItem }) => {
  renderItem = renderItem || CommunityItem;
  return (
    <ul className="list-unstyled">
      {communities.map((community) => (
        <li key={community.id}>{renderItem({ community })}</li>
      ))}
    </ul>
  );
};

const App = () => {
  return (
    <>
      <CommunityGallery communities={__RECORD_COMMUNITIES.accepted || []} />
      <Accordion
        panels={[
          {
            key: "pending-requests",
            title: "Pending requests",
            content: {
              content: (
                <>
                  <CommunityGallery
                    renderItem={CommunityPendingItem}
                    communities={__RECORD_COMMUNITIES.pending || []}
                  />
                  <CommunityRequestModal />
                </>
              ),
            },
          },
        ]}
      />
    </>
  );
};

const domContainer = document.querySelector("#communities-management");
const __RECORD = JSON.parse(domContainer.dataset.record);
const __RECORD_COMMUNITIES = JSON.parse(domContainer.dataset.communities);
ReactDOM.render(<App />, domContainer);
