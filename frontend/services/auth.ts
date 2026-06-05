import { apiClient } from "./api-client";
import type { UserResponse, TokenResponse } from "@/types";

export const authService = {
  async register(email: string, username: string, password: string): Promise<UserResponse> {
    return apiClient.post<UserResponse>("/auth/register", { email, username, password });
  },

  async login(username: string, password: string): Promise<TokenResponse> {
    return apiClient.post<TokenResponse>("/auth/login", { username, password });
  },

  async getMe(): Promise<UserResponse> {
    return apiClient.get<UserResponse>("/auth/me");
  },
};
