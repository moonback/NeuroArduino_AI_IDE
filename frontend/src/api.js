import axios from 'axios';

const DEFAULT_API_BASE = 'http://127.0.0.1:8001';
const rawBase = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE;
const API_BASE_URL = rawBase.replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const buildWsUrl = (path) => {
  const wsProtocol = API_BASE_URL.startsWith('https://') ? 'wss://' : 'ws://';
  const wsBase = API_BASE_URL.replace(/^https?:\/\//, wsProtocol);
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${wsBase}${normalizedPath}`;
};

export { API_BASE_URL };
export default api;
