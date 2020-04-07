import React from "react";
import { useEffect, Component } from "react";
import ReactDOM from "react-dom";
import axios from "axios";

import "semantic-ui-css/semantic.min.css";

var listCommunities = (successHandler, errorHandler) => {
  axios
  .get(`/api/communities/`)
  .then(function (response) {
    successHandler(response.data)
  })
  .catch(error => {
    console.log(error)
  })
}

class Popup extends React.Component {
  render() {
    return (
      <div className="popup">
        <div className="popup\_inner">
          <h5><b>{this.props.text}</b></h5>
          {/* <button onClick={this.props.closePopup}></button> */}
        </div>
      </div>
    );
  }
}

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
    <>
    { communities ? (
      communities.map((c) => {
        <a onClick={onSelect(c.id)}><p>{c.id}</p></a>
      })
    ) : null }
    </>
  )
}


const App = (props) => {
  const [showPopup, setShowPopup] = useState(false);
  const [community, setCommunity] = useState(null);

  function onCommunitySelectHandler(community_id) {
    setCommunity(community_id);
    setShowPopup(false);
  }

  return (
    <div>
      <button className="ui button" onClick={setShowPopup(!showPopup)}>
        {" Request this record "}
      </button>

      {showPopup ? (
        <Popup
          text='In which community do you want to add it?'
          closePopup={setShowPopup(false)}
        >
          <CommunitySelectList onSelect={onCommunitySelectHandler} />
        </Popup>
      ) : null}
    </div>
  );
}


class App extends Component {
  constructor(props) {
    super(props);
    this.state = { showPopup: false };
  }

  togglePopup() {
    this.setState({
      showPopup: !this.state.showPopup
    });
  }

  render() {
    return (
      <div>
        <button className="ui button" onClick={this.togglePopup.bind(this)}>
          {" Request this record "}
        </button>

        {this.state.showPopup ? (
          <Popup
            text='In which community do you want to add it?'
            closePopup={this.togglePopup.bind(this)}
          />
        ) : null}
      </div>
    );
  }
}

export default App;

const domContainer = document.querySelector("#communities-management");
ReactDOM.render(<App />, domContainer);
