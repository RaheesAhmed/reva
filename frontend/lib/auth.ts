
import Cookies from 'js-cookie';

interface AuthResponse {
  message: string;
  email: string;
  user?: any;
  access_token?: string;
  refresh_token?: string;
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

export async function registerUser(data: {
  email: string;
  password: string;
  name: string;
}): Promise<AuthResponse> {
  const response = await fetch(`/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}

export function setAuthCookies(data: AuthResponse) {
  if (!data.access_token || !data.refresh_token) return;
  
  // Set the main auth token
  Cookies.set('token', data.access_token, { 
    expires: 7, // 7 days
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict'
  });
  
  // Set the refresh token
  Cookies.set('refresh_token', data.refresh_token, {
    expires: 30, // 30 days
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict'
  });
}

export function getUserToken(): string | null {
  return Cookies.get('token') || null;
}

export function getRefreshToken(): string | null {
  return Cookies.get('refresh_token') || null;
}

export function logout() {
  // Remove all auth-related cookies
  Cookies.remove('token');
  Cookies.remove('refresh_token');
  
  // Force a page refresh to clear any cached state
  window.location.href = '/login';
}
