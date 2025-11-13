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
  const config = data instanceof FormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : undefined;
  if (id) {
    const response = await apiClient.patch(`accounts/profiles/${id}/`, data, config);
    return response.data;
  }
  const response = await apiClient.post('accounts/profiles/', data, config);
  return response.data;
}

export async function fetchNotifications(params = {}) {
  const response = await apiClient.get('accounts/notifications/', { params });
  return response.data;
}

export async function markNotificationRead(id) {
  const response = await apiClient.post(`accounts/notifications/${id}/mark_read/`);
  return response.data;
}

export async function markAllNotificationsRead() {
  const response = await apiClient.post('accounts/notifications/mark_all_read/');
  return response.data;
}

export async function fetchWallet(params = {}) {
  const response = await apiClient.get('accounts/wallets/', { params });
  return response.data;
}

export async function depositWallet(payload) {
  const response = await apiClient.post('accounts/wallets/deposit/', payload);
  return response.data;
}

export async function withdrawWallet(payload) {
  const response = await apiClient.post('accounts/wallets/withdraw/', payload);
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

export async function reviewApplication(id, action) {
  const response = await apiClient.post(`marketplace/applications/${id}/${action}/`);
  return response.data;
}

export async function fetchContracts(params = {}) {
  const response = await apiClient.get('marketplace/contracts/', { params });
  return response.data;
}

export async function signContract(id) {
  const response = await apiClient.post(`marketplace/contracts/${id}/sign/`);
  return response.data;
}

export async function completeContract(id) {
  const response = await apiClient.post(`marketplace/contracts/${id}/complete/`);
  return response.data;
}

export async function requestContractTermination(id, payload) {
  const response = await apiClient.post(`marketplace/contracts/${id}/request_termination/`, payload);
  return response.data;
}

export async function approveContractTermination(id) {
  const response = await apiClient.post(`marketplace/contracts/${id}/approve_termination/`);
  return response.data;
}

export async function submitVerification(payload) {
  const response = await apiClient.post('accounts/verifications/', payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function fetchVerificationRequests(params = {}) {
  const response = await apiClient.get('accounts/verifications/', { params });
  return response.data;
}

export async function reviewVerificationRequest(id, action, payload = {}) {
  const response = await apiClient.post(
    `accounts/verifications/${id}/${action}/`,
    payload,
  );
  return response.data;
}
