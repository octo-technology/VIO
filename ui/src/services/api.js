import axios from "axios";

const api_url = "http://" + location.hostname + ":8000/api/v1";

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
