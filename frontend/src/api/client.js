import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/`,
  withCredentials: true,
});

export function applyAuthToken(token) {
  if (token) {
    apiClient.defaults.headers.common.Authorization = `Token ${token}`;
  } else {
    delete apiClient.defaults.headers.common.Authorization;
  }
}

export async function registerUser(payload) {
  const response = await apiClient.post('accounts/register/', payload);
  return response.data;
}

export async function login(payload) {
  const response = await apiClient.post('accounts/login/', payload);
  return response.data;
}

export async function logout() {
  return apiClient.post('accounts/logout/');
}

export async function fetchProfile() {
  const response = await apiClient.get('accounts/profiles/me/');
  return response.data;
}

export async function upsertProfile(data, id) {
  if (id) {
    const response = await apiClient.patch(`accounts/profiles/${id}/`, data);
    return response.data;
  }
  const response = await apiClient.post('accounts/profiles/', data);
  return response.data;
}

export async function fetchCategories() {
  const response = await apiClient.get('marketplace/categories/');
  return response.data;
}

export async function fetchSkills(params = {}) {
  const response = await apiClient.get('marketplace/skills/', { params });
  return response.data;
}

export async function fetchOrders(params = {}) {
  const response = await apiClient.get('marketplace/orders/', { params });
  return response.data;
}

export async function fetchOrder(id) {
  const response = await apiClient.get(`marketplace/orders/${id}/`);
  return response.data;
}

export async function createOrder(payload) {
  const response = await apiClient.post('marketplace/orders/', payload);
  return response.data;
}

export async function applyToOrder(payload) {
  const response = await apiClient.post('marketplace/applications/', payload);
  return response.data;
}

export async function submitVerification(payload) {
  const response = await apiClient.post('accounts/verifications/', payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}
