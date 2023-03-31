import axios from "axios";

function isEnvVariableDefine(envVariable) {
  return envVariable == "" || envVariable == undefined;
}

const envProtocol = process.env.VUE_APP_API_PROTOCOL;
const protocol = isEnvVariableDefine(envProtocol) ? "http" : envProtocol;

const env_hostname = process.env.VUE_APP_API_HOSTNAME;
const hostname = isEnvVariableDefine(env_hostname)
  ? location.hostname
  : env_hostname;

const env_port = process.env.VUE_APP_API_PORT;
const port = isEnvVariableDefine(env_port) ? 8000 : env_port;

const apiURL =
  protocol == "http"
    ? `${protocol}://${hostname}:${port}`
    : `${protocol}://${hostname}`;

export const baseURL = apiURL + "/api/v1";
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
