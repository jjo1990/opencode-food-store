import client from './client';
import type { AxiosResponse } from 'axios';

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

export const authApi = {
  postRegister: async (
    email: string,
    password: string,
    fullName: string
  ): Promise<UserResponse> => {
    const response: AxiosResponse<UserResponse> = await client.post<UserResponse>(
      '/auth/register',
      {
        email,
        password,
        full_name: fullName,
      }
    );
    return response.data;
  },

  postLogin: async (email: string, password: string): Promise<TokenResponse> => {
    const response = await client.post<TokenResponse>('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  postRefresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await client.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  postLogout: async (refreshToken: string): Promise<void> => {
    await client.post('/auth/logout', {
      refresh_token: refreshToken,
    });
  },
};

export default client;
