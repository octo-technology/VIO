import axios from "axios";

const env_hostname = process.env.VUE_APP_API_HOSTNAME;
const hostname =
  env_hostname == "" || env_hostname == undefined
    ? location.hostname
    : env_hostname;
const env_port = process.env.VUE_APP_API_PORT;
const port = env_port == "" || env_port == undefined ? 8000 : env_port;
const api_url = `http://${hostname}:${port}/api/v1`;

export const baseURL = api_url;
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
