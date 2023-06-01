import axios from 'axios'

function isEnvVariableDefine(envVariable) {
  return envVariable === '' || envVariable === undefined
}

const envProtocol = process.env.VUE_APP_API_PROTOCOL
const protocol = isEnvVariableDefine(envProtocol) ? 'http' : envProtocol

const envHostname = process.env.VUE_APP_API_HOSTNAME
const hostname = isEnvVariableDefine(envHostname) ? location.hostname : envHostname // eslint-disable-line

const envPort = process.env.VUE_APP_API_PORT
const port = isEnvVariableDefine(envPort) ? 8000 : envPort

const apiURL = protocol === 'http' ? `${protocol}://${hostname}:${port}` : `${protocol}://${hostname}`

export const baseURL = `${apiURL}/api/v1`

export default () => {
  return axios.create({
    baseURL,
    withCredentials: false,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json'
    }
  })
}
