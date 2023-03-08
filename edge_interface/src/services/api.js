import axios from "axios";

const envProtocol = process.env.VUE_APP_PROTOCOL;
const protocol = envProtocol !== "" ? envProtocol : "http";
const envHostname = process.env.VUE_APP_API_HOSTNAME;
const hostname = envHostname !== "" ? envHostname : location.hostname;
const envPort = process.env.VUE_APP_API_PORT;
const port = envPort !== "" ? envPort : 8000;
const apiURL =
  protocol == "http"
    ? `${protocol}://${hostname}:${port}`
    : `${protocol}://${hostname}`;
const completeApiURL = apiURL + "/api/v1";

export const baseURL = completeApiURL;
console.log(`Server listening on: ${baseURL}`);

export default () => {
  return axios.create({
    baseURL: baseURL,
    withCredentials: false,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    }
  });
};
