import { create } from 'zustand';
import { authAPI } from '../services/api';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authAPI.login(username, password);
      
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      set({
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erro ao fazer login';
      set({
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      await authAPI.register(userData);
      set({ isLoading: false, error: null });
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erro ao registrar';
      set({ isLoading: false, error: errorMessage });
      return { success: false, error: errorMessage };
    }
  },

  logout: () => {
    authAPI.logout();
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    });
  },

  checkAuth: () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      set({ isAuthenticated: true });
    }
  },

  clearError: () => set({ error: null }),
}));
