import axios from 'axios';

const backendBaseURL =
  import.meta.env.VITE_BACKEND_URL ||
  (window?.location?.protocol === 'file:' ? 'http://127.0.0.1:8001' : `${window.location.protocol}//${window.location.hostname}:8001`);

export const api = axios.create({
  baseURL: backendBaseURL,
  timeout: 10000,
  withCredentials: false,
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config || {};
    if (!config.__retryCount) config.__retryCount = 0;

    const isRetriable = !error.response && config.__retryCount < 1;
    if (isRetriable) {
      config.__retryCount += 1;
      return api(config);
    }

    return Promise.reject(error);
  }
);

export const wsMonitorUrl = () => {
  const url = new URL(backendBaseURL);
  const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${url.host}/ws/monitor`;
};
