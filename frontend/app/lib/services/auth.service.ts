import { http } from '../api/http';
import { ENDPOINTS } from '../api/endpoints';
import { tokenStorage } from '../storage/token.storage';

type LoginPayload = {
  email: string;
  password: string;
};

export async function login(payload: LoginPayload) {
  const response = await http.post(ENDPOINTS.AUTH.LOGIN, payload);

  // ⚠️ FORMAT BACKEND
  const token = response.data?.data?.access_token;

  if (!token) {
    throw new Error('Token manquant dans la réponse');
  }

  tokenStorage.set(token);
  return token;
}

export async function getMe() {
  const response = await http.get(ENDPOINTS.AUTH.ME);
  return response.data?.data;
}

export async function register(payload: {
  email: string;
  password: string;
  role: string;
}) {
  const response = await http.post(ENDPOINTS.AUTH.REGISTER, payload);

  const token = response.data?.data?.access_token;

  if (!token) {
    throw new Error('Token manquant dans la réponse register');
  }

  tokenStorage.set(token);
  return token;
}

export function logout() {
  tokenStorage.clear();
}
