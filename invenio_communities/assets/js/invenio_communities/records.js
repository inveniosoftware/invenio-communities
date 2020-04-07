import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import axios from "axios";

import "semantic-ui-css/semantic.min.css";
import { Accordion, Icon } from 'semantic-ui-react'

var listCommunities = (successHandler, errorHandler) => {
  axios
  .get(`/api/communities/`)
  .then(function (response) {
    console.log(response.data)
    successHandler(response.data)
  })
  .catch(error => {
    console.log(error)
  })
}

// const Popup = ({text, closePopup}) => {
//   return (
//     <div className="popup">
//       <div className="popup\_inner">
//         <h5><b>{text}</b></h5>
//         <button onClick={closePopup}></button>
//       </div>
//     </div>
//   )
// };

function useCommunitySelect() {
  const [communities, setCommunuties] = useState(null);
  useEffect(() => {
    return listCommunities(setCommunuties);
  }, [])
  return [communities]
}

const CommunitySelectList = ({ onSelect }) => {
  const [communities] = useCommunitySelect();

  return (
    <div>
    { communities ? (
      communities.hits.hits.map((c) => (
      <a key={c.metadata.id} onClick={() => onSelect(c.metadata.id)}><p>[{c.metadata.id}] - {c.metadata.title}</p></a>
      ))
    ) : null }
    </div>
  )
}


const panels = [
  {
    key: 'pending-requests',
    title: 'Pending requests',
    content: 'Here is the list of the pending requests',
  },
  {
    key: 'accepted-requests',
    title: 'Accepted requests',
    content: 'Here is the list of the accepted requests',
  },
  {
    key: 'rejected-requests',
    title: 'Rejected-requests',
    content: 'Here is the list of the rejected requests',
},
]

const App = (props) => {
  const [showPopup, setShowPopup] = useState(false);
  const [community, setCommunity] = useState(null);

  function onCommunitySelectHandler(community_id) {
    setCommunity(community_id);
    setShowPopup(false);
  }
  console.log('here I am')

  return (
    <div>
      <h4>Available communities</h4>
      <CommunitySelectList onSelect={onCommunitySelectHandler} />
      <h4>Your requests</h4>
      <Accordion defaultActiveIndex={0} panels={panels} />
      {/* <button className="ui button" onClick={() => setShowPopup(!showPopup)}>
        {"Request this record "}
      </button>

      {showPopup ? (
        <div>
          <Popup
            text='In which community do you want to add it?'
            closePopup={() => setShowPopup(false)}
          />
        </div>
      ) : null}
    </div> */}
    </div>
  );
}

const domContainer = document.querySelector("#communities-management");
ReactDOM.render(<App />, domContainer);
