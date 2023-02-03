import React from "react";
import ReactDOM from "react-dom";
import { CurationPolicyForm } from "./CurationPolicyForm";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);

ReactDOM.render(<CurationPolicyForm community={community} />, domContainer);
