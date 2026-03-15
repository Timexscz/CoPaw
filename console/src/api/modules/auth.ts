import { request } from "../request";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuthStatus {
  enabled: boolean;
  allow_registration: boolean;
  authenticated: boolean;
  user: User | null;
}

export const authApi = {
  /**
   * Login with username and password
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    return request.post("/auth/login", data);
  },

  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    return request.post("/auth/register", data);
  },

  /**
   * Logout (client should discard token)
   */
  async logout(): Promise<{ message: string }> {
    return request.post("/auth/logout");
  },

  /**
   * Get current user info
   */
  async getMe(): Promise<User> {
    return request.get("/auth/me");
  },

  /**
   * Get authentication status
   */
  async getStatus(): Promise<AuthStatus> {
    return request.get("/auth/status");
  },
};

export default authApi;
