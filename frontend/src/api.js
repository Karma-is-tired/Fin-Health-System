// Everything that talks to the backend lives here.
export const API_BASE = import.meta.env.VITE_API_BASE || 'https://fin-health-system.onrender.com';

// Change this one line to change the currency shown everywhere.
export const CURRENCY = '₦';

export const money = (n) =>
  `${CURRENCY}${Number(n ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

export const bandOf = (score) => (score >= 71 ? 'Strong' : score >= 41 ? 'Moderate' : 'Weak');

const TOKEN_KEY = 'token';
export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

function readPayload(token) {
  try {
    const part = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(part));
  } catch {
    return null;
  }
}

// Only used to decide what to show; the server checks the token for real.
export function isLoggedIn() {
  const payload = readPayload(getToken() || '');
  return Boolean(payload) && (!payload.exp || payload.exp * 1000 > Date.now());
}

export function currentEmail() {
  return readPayload(getToken() || '')?.sub || '';
}

const NETWORK_MESSAGE =
  "Can't reach the server. If it has been idle it may be waking up, so wait a minute and try again.";

async function readError(res, fallback) {
  const data = await res.json().catch(() => ({}));
  return typeof data.detail === 'string' ? data.detail : fallback;
}

async function authRequest(path, options) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new Error(NETWORK_MESSAGE);
  }
  if (!res.ok) throw new Error(await readError(res, 'Something went wrong. Please try again.'));
  const data = await res.json();
  setToken(data.access_token);
}

export const signIn = (email, password) =>
  authRequest('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  });

export const signUp = (email, password) =>
  authRequest('/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

export function signOut() {
  clearToken();
  window.location.assign('/login');
}

// Fetch with the login token attached. An expired session sends you back to sign in.
export async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error(NETWORK_MESSAGE);
  }
  if (res.status === 401) {
    signOut();
    throw new Error('Your session has expired. Please sign in again.');
  }
  return res;
}

export async function apiJson(path, options) {
  const res = await apiFetch(path, options);
  if (!res.ok) throw new Error(await readError(res, 'Request failed. Please try again.'));
  return res.json();
}

export async function downloadFile(path, filename) {
  const res = await apiFetch(path);
  if (!res.ok) throw new Error(await readError(res, 'Download failed. Please try again.'));
  const url = window.URL.createObjectURL(await res.blob());
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export function monthLabel(yyyyMm) {
  const date = new Date(`${yyyyMm}-01T00:00:00`);
  return Number.isNaN(date.getTime())
    ? yyyyMm
    : date.toLocaleString('en', { month: 'short', year: '2-digit' });
}
