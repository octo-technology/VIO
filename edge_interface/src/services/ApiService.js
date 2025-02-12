import axios from 'axios';

function isEnvVariableDefined(envVariable) {
  return envVariable !== '' && envVariable !== undefined;
}

const envProtocol = process.env.VUE_APP_API_PROTOCOL;
const protocol = isEnvVariableDefined(envProtocol) ? envProtocol : 'http';

const envHostname = process.env.VUE_APP_API_HOSTNAME;
const hostname = isEnvVariableDefined(envHostname) ? envHostname : location.hostname; // eslint-disable-line

const envPort = process.env.VUE_APP_API_PORT;
const port = isEnvVariableDefined(envPort) ? envPort : 8000;

const apiURL = protocol === 'http' ? `${protocol}://${hostname}:${port}` : `${protocol}://${hostname}`;

export const baseURL = `${apiURL}/api/v1`;

const apiClient = axios.create({
  baseURL,
  withCredentials: false,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
});

apiClient.interceptors.response.use(
  response => response,
  error => {
    if (!error.response) {
      // Network error (e.g., backend is not available)
      error.message = 'Backend is not available. Please start or check the backend.';
    }
    return Promise.reject(error);
  }
);

export default {
  getItems() {
    return apiClient.get('/items');
  },
  getItem(itemId) {
    return apiClient.get(`/items/${itemId}`);
  },
  getItemImage(itemId, cameraId) {
    return `${baseURL}/items/${itemId}/binaries/${cameraId}`;
  },
  triggerApi() {
    return apiClient.post('/trigger');
  },
  getConfigs() {
    return apiClient.get('/configs');
  },
  getActiveConfig() {
    return apiClient.get('/configs/active');
  },
  setActiveConfig(config) {
    return apiClient.post('/configs/active', config);
  },
  setActiveConfigByName(stationName) {
    return apiClient.post('/configs/active?station_name=' + stationName);
  }
};