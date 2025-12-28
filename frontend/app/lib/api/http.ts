import axios from 'axios';
import { ENV } from '../env';
import { tokenStorage } from '../storage/token.storage';

export const http = axios.create({
  baseURL: ENV.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Inject JWT
http.interceptors.request.use((config) => {
  const token = tokenStorage.get();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Gestion erreurs globale
http.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      tokenStorage.clear();
    }
    return Promise.reject(err);
  }
);
