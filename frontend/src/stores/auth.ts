import { computed, ref } from 'vue';
import { api } from '../services/api';
import type { User } from '../types';

const token = ref<string | null>(localStorage.getItem('myaloca_token'));
const currentUser = ref<User | null>(null);
const isLoading = ref<boolean>(false);
const authError = ref<string | null>(null);

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value && !!currentUser.value);
  const isAdmin = computed(
    () => currentUser.value?.role === 'admin' || currentUser.value?.role === 'gestor'
  );

  async function login(email: string, pass: string) {
    isLoading.value = true;
    authError.value = null;
    try {
      const res = await api.auth.login(email, pass);
      token.value = res.access_token;
      localStorage.setItem('myaloca_token', res.access_token);
      await fetchMe();
    } catch (err: any) {
      authError.value = err.message || 'Falha ao autenticar';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchMe() {
    if (!token.value) return;
    try {
      currentUser.value = await api.auth.getMe();
    } catch {
      logout();
    }
  }

  function logout() {
    token.value = null;
    currentUser.value = null;
    localStorage.removeItem('myaloca_token');
  }

  async function register(userData: Partial<User> & { password: string }) {
    isLoading.value = true;
    authError.value = null;
    try {
      await api.auth.register(userData);
      await login(userData.email!, userData.password);
    } catch (err: any) {
      authError.value = err.message || 'Falha ao cadastrar conta';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateProfile(userData: Partial<User> & { password?: string }) {
    isLoading.value = true;
    authError.value = null;
    try {
      const updated = await api.auth.updateMe(userData);
      currentUser.value = updated;
      return updated;
    } catch (err: any) {
      authError.value = err.message || 'Falha ao atualizar perfil';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function switchDemoUser(role: 'admin' | 'colaborador' | 'mariana' | 'rodrigo') {
    if (role === 'admin') {
      await login('admin@myaloca.com', 'admin123');
    } else if (role === 'mariana') {
      await login('mariana@myaloca.com', 'mariana123');
    } else if (role === 'rodrigo') {
      await login('rodrigo@myaloca.com', 'rodrigo123');
    } else {
      await login('colaborador@myaloca.com', 'colab123');
    }
  }

  async function initAuth() {
    if (token.value) {
      await fetchMe();
    }
  }

  return {
    token,
    currentUser,
    isLoading,
    authError,
    isAuthenticated,
    isAdmin,
    login,
    register,
    updateProfile,
    logout,
    fetchMe,
    switchDemoUser,
    initAuth,
  };
}
