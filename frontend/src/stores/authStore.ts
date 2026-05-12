/**
 * Auth Store - Zustand store for authentication state
 * Following FSD: stores/ directory
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, type TokenResponse, type UserResponse } from '../shared/api/authApi';

interface User {
  id: string;
  email: string;
  roles: string[];
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  setTokens: (tokens: TokenResponse) => void;
  clearTokens: () => void;
  setUser: (user: User) => void;
  initializeFromStorage: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      isLoading: false,
      error: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await authApi.postLogin(email, password);
          get().setTokens(tokens);

          // Decode user from access token (simplified)
          // In production, you'd have a /me endpoint
          const userPayload = JSON.parse(atob(tokens.access_token.split('.')[1]));
          set({
            user: {
              id: userPayload.sub,
              email: email,
              roles: userPayload.roles || ['CLIENT'],
            },
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Login failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      register: async (email: string, password: string, fullName: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.postRegister(email, password, fullName);
          // After register, redirect to login
          set({ isLoading: false });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Registration failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        const { accessToken } = get();
        try {
          if (accessToken) {
            // Try to revoke refresh token, but don't fail if it doesn't work
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              await authApi.postLogout(refreshToken).catch(() => {});
            }
          }
        } finally {
          get().clearTokens();
          set({ user: null, isAuthenticated: false, error: null });
        }
      },

      setTokens: (tokens: TokenResponse) => {
        localStorage.setItem('refreshToken', tokens.refresh_token);
        set({ accessToken: tokens.access_token });
      },

      clearTokens: () => {
        localStorage.removeItem('refreshToken');
        set({ accessToken: null });
      },

      setUser: (user: User) => {
        set({ user, isAuthenticated: true });
      },

      initializeFromStorage: async () => {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          return;
        }

        set({ isLoading: true });
        try {
          const tokens = await authApi.postRefresh(refreshToken);
          get().setTokens(tokens);

          const userPayload = JSON.parse(atob(tokens.access_token.split('.')[1]));
          set({
            user: {
              id: userPayload.sub,
              email: userPayload.email || '',
              roles: userPayload.roles || ['CLIENT'],
            },
            isAuthenticated: true,
            isLoading: false,
          });
        } catch {
          // Token expired or invalid - clear storage
          get().clearTokens();
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ refreshToken: localStorage.getItem('refreshToken') }), // Persist refreshToken in localStorage
    }
  )
);