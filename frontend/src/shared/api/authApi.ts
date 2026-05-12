/**
 * Auth API Client - Axios wrapper for auth endpoints
 * Following FSD: shared/api/ directory
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import toast from 'react-hot-toast';
import { useAuthStore } from '../../stores/authStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  roles: string[];
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = useAuthStore.getState().accessToken;
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors with toasts
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const status = error.response?.status;
    const message = error.response?.data?.detail || error.message;

    let toastMessage = 'An error occurred';

    switch (status) {
      case 401:
        toastMessage = 'Sesión expirada. Por favor, inicia sesión nuevamente.';
        // Clear tokens on 401 (token expired or invalid)
        useAuthStore.getState().clearTokens();
        break;
      case 403:
        toastMessage = 'No tienes permiso para realizar esta acción.';
        break;
      case 422:
        toastMessage = message || 'Error de validación.';
        break;
      case 409:
        toastMessage = 'Este recurso ya existe.';
        break;
      case 429:
        toastMessage = 'Demasiados intentos. Por favor, espera 15 minutos.';
        break;
      case 500:
        toastMessage = 'Error del servidor. Intenta más tarde.';
        break;
      default:
        if (error.code === 'ECONNABORTED') {
          toastMessage = 'Tiempo de espera agotado. Intenta de nuevo.';
        } else if (!error.response) {
          toastMessage = 'Error de conexión. Verifica tu internet.';
        }
    }

    toast.error(toastMessage);
    return Promise.reject(error);
  }
);

// Auth API functions
export const authApi = {
  postRegister: async (email: string, password: string, fullName: string): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/auth/register', {
      email,
      password,
      full_name: fullName,
    } as RegisterRequest);
    return response.data;
  },

  postLogin: async (email: string, password: string): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/login', {
      email,
      password,
    } as LoginRequest);
    return response.data;
  },

  postRefresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  postLogout: async (refreshToken: string): Promise<void> => {
    await api.post('/auth/logout', {
      refresh_token: refreshToken,
    });
  },
};

export default api;