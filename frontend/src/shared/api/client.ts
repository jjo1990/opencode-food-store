/// <reference types="vite/client" />
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import toast from 'react-hot-toast';
import { useAuthStore } from '../../stores/authStore';
import { devLogger } from '../utils/logger';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = useAuthStore.getState().accessToken;
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

client.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      const method = response.config.method?.toUpperCase() ?? 'UNKNOWN';
      const url = response.config.url ?? 'UNKNOWN';
      devLogger.debug('API Response', {
        method,
        url,
        status: response.status,
      });
    }
    return response;
  },
  (error: AxiosError<{ detail?: string }>) => {
    const status = error.response?.status;
    const message = error.response?.data?.detail || error.message;

    let toastMessage: string | null = 'Ocurrió un error';

    switch (status) {
      case 401: {
        const { accessToken, clearTokens } = useAuthStore.getState();
        // Si tenía un token activo y el backend lo rechazó -> sesión expirada
        if (accessToken) {
          toastMessage = 'Sesión expirada. Por favor, inicia sesión nuevamente.';
          clearTokens();
        } else {
          // Sin token activo: 401 es esperable (login inválido) -> no mostrar toast
          toastMessage = null;
        }
        break;
      }
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

    if (toastMessage) {
      toast.error(toastMessage);
    }
    return Promise.reject(error);
  }
);

export default client;
