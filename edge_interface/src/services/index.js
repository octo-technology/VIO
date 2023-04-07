import ConfigApiService from './configApi.service';

window.env = window.env || {};

const configApiHost = window.env.CONFIG_API_HOST ? window.env.CONFIG_API_HOST : 'http://localhost:8080'

const configApiService = new ConfigApiService({ configApiHost });

export { configApiService };
