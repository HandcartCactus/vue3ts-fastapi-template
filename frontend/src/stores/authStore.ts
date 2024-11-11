// store/auth.ts
import { defineStore } from 'pinia';
import {Token} from '@/services/authService'

interface AuthState {
  username: string | null;
  token: Token | null;
  isAuthenticated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    username: null,
    token: null,
    isAuthenticated: false,
  }),

  actions: {
    login(username: string, token: Token) {
      this.username = username;
      this.token = token;
      this.isAuthenticated = true;
    },

    logout() {
      this.username = null;
      this.token = null;
      this.isAuthenticated = false;
    },
  },

  getters: {
    isLoggedIn: (state): boolean => state.isAuthenticated,
    getTokenStr: (state): string => {
      if (state.token) {
        return state.token.token;
      }
      throw new Error('No token available');
    }
  },
});
