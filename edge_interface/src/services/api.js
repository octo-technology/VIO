import axios from "axios";

const env_hostname = process.env.VUE_APP_API_HOSTNAME;
const hostname = env_hostname !== "" ? env_hostname : location.hostname;
const api_url = "http://" + hostname + ":8000/api/v1";

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
