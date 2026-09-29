<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  Lock,
  Mail,
  User as UserIcon,
  Briefcase,
  Building,
  Sparkles,
  ArrowRight,
  LogOut,
  Image as ImageIcon,
  Edit3,
  Check,
} from 'lucide-vue-next';
import { api } from '../services/api';
import { useAuth } from '../stores/auth';
import type { Department } from '../types';

const emit = defineEmits<{
  (e: 'login-success'): void;
}>();

const {
  currentUser,
  isAuthenticated,
  login,
  register,
  updateProfile,
  logout,
  switchDemoUser,
  isLoading,
  authError,
} = useAuth();

const activeTab = ref<'login' | 'register' | 'profile'>(
  isAuthenticated.value ? 'profile' : 'login'
);

// Login form state
const loginEmail = ref('');
const loginPassword = ref('');
const loginError = ref<string | null>(null);

// Register form state
const regFullName = ref('');
const regEmail = ref('');
const regPassword = ref('');
const regJobTitle = ref('');
const regDepartment = ref('Engenharia');
const regRole = ref<'colaborador' | 'admin'>('colaborador');
const regAvatarUrl = ref('https://api.dicebear.com/7.x/bottts/svg?seed=Alex');
const regCustomPhoto = ref('');
const regError = ref<string | null>(null);

// Avatar Presets
const avatarPresets = [
  { name: 'Alex Bot', url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Alex' },
  { name: 'Sam Bot', url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Sam' },
  { name: 'Luna Bot', url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Luna' },
  { name: 'Dev Neo', url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Neo' },
  { name: 'Aria Bot', url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Aria' },
  { name: 'Atlas Bot', url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Atlas' },
];

// Dynamic Departments
const dbDepartments = ref<Department[]>([]);
const defaultDepartments = [
  'Engenharia & Tecnologia',
  'Design & UX',
  'Produto & Estratégia',
  'Operações & Facilities',
  'Data & Analytics',
  'Recursos Humanos & People',
  'Comercial & Vendas',
  'Financeiro & Jurídico',
];

const departmentOptions = computed(() => {
  if (dbDepartments.value.length === 0) return defaultDepartments;
  const fromDb = dbDepartments.value.map((d) => d.name);
  return Array.from(new Set([...fromDb, ...defaultDepartments])).sort();
});

onMounted(async () => {
  try {
    dbDepartments.value = await api.departments.list();
  } catch {
    // fallback
  }
});

const selectedAvatarPreview = computed(() => {
  if (regCustomPhoto.value.trim()) {
    return regCustomPhoto.value.trim();
  }
  return regAvatarUrl.value;
});

// Profile edit state
const isEditingProfile = ref(false);
const editFullName = ref('');
const editJobTitle = ref('');
const editDepartment = ref('Engenharia');
const editAvatarUrl = ref('https://api.dicebear.com/7.x/bottts/svg?seed=Alex');
const editCustomPhoto = ref('');
const editPassword = ref('');
const editError = ref<string | null>(null);
const editSuccess = ref(false);
const isSavingProfile = ref(false);

function startEditingProfile() {
  if (!currentUser.value) return;
  editFullName.value = currentUser.value.full_name || '';
  editJobTitle.value = currentUser.value.job_title || '';
  editDepartment.value = currentUser.value.department || 'Engenharia';
  editAvatarUrl.value =
    currentUser.value.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=Alex';
  editCustomPhoto.value = currentUser.value.photo_url || '';
  editPassword.value = '';
  editError.value = null;
  editSuccess.value = false;
  isEditingProfile.value = true;
}

const editAvatarPreview = computed(() => {
  if (editCustomPhoto.value.trim()) {
    return editCustomPhoto.value.trim();
  }
  return editAvatarUrl.value;
});

async function handleSaveProfile() {
  isSavingProfile.value = true;
  editError.value = null;
  editSuccess.value = false;

  try {
    const payload: any = {
      full_name: editFullName.value,
      job_title: editJobTitle.value,
      department: editDepartment.value,
      avatar_url: editAvatarUrl.value,
      photo_url: editCustomPhoto.value.trim() || null,
    };
    if (editPassword.value.trim()) {
      payload.password = editPassword.value.trim();
    }
    await updateProfile(payload);
    editSuccess.value = true;
    setTimeout(() => {
      isEditingProfile.value = false;
      editSuccess.value = false;
    }, 1200);
  } catch (err: any) {
    editError.value = err.message || 'Falha ao atualizar perfil';
  } finally {
    isSavingProfile.value = false;
  }
}

async function handleLogin() {
  loginError.value = null;
  try {
    await login(loginEmail.value, loginPassword.value);
    emit('login-success');
  } catch (err: any) {
    loginError.value = err.message || 'Falha ao autenticar usuário';
  }
}

async function handleDemoLogin(role: 'admin' | 'colaborador' | 'mariana' | 'rodrigo') {
  loginError.value = null;
  try {
    await switchDemoUser(role);
    emit('login-success');
  } catch (err: any) {
    loginError.value = err.message || 'Falha ao logar com perfil demo';
  }
}

async function handleRegister() {
  regError.value = null;
  try {
    await register({
      full_name: regFullName.value,
      email: regEmail.value,
      password: regPassword.value,
      job_title: regJobTitle.value || 'Colaborador',
      department: regDepartment.value,
      role: regRole.value,
      avatar_url: regAvatarUrl.value,
      photo_url: regCustomPhoto.value.trim() || null,
    });
    emit('login-success');
  } catch (err: any) {
    regError.value = err.message || 'Falha ao registrar usuário';
  }
}

function handleLogout() {
  logout();
  activeTab.value = 'login';
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-8 space-y-6">
    <!-- Header -->
    <div class="text-center space-y-2">
      <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold">
        <Sparkles class="w-3.5 h-3.5" />
        <span>Autenticação & Identidade Digital</span>
      </div>
      <h2 class="text-2xl font-bold tracking-tight text-ink">
        Acesse sua Estação no MyAloca
      </h2>
      <p class="text-xs text-ink-subtle max-w-md mx-auto">
        Entre com sua conta para reservar baias, visualizar seu avatar no mapa 3D e realizar check-ins presenciais.
      </p>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center justify-center space-x-1 bg-surface-2 p-1 rounded-xl border border-hairline max-w-sm mx-auto">
      <button
        v-if="!isAuthenticated"
        class="flex-1 py-1.5 px-4 text-xs font-semibold rounded-lg transition"
        :class="activeTab === 'login' ? 'bg-surface-1 text-ink shadow-sm' : 'text-ink-subtle hover:text-ink'"
        @click="activeTab = 'login'"
      >
        Entrar
      </button>
      <button
        v-if="!isAuthenticated"
        class="flex-1 py-1.5 px-4 text-xs font-semibold rounded-lg transition"
        :class="activeTab === 'register' ? 'bg-surface-1 text-ink shadow-sm' : 'text-ink-subtle hover:text-ink'"
        @click="activeTab = 'register'"
      >
        Cadastrar
      </button>
      <button
        v-if="isAuthenticated"
        class="flex-1 py-1.5 px-4 text-xs font-semibold rounded-lg transition"
        :class="activeTab === 'profile' ? 'bg-surface-1 text-ink shadow-sm' : 'text-ink-subtle hover:text-ink'"
        @click="activeTab = 'profile'"
      >
        Meu Perfil Ativo
      </button>
    </div>

    <!-- TAB 1: LOGIN -->
    <div v-if="activeTab === 'login'" class="bg-surface-1 border border-hairline rounded-2xl p-6 shadow-xl space-y-6">
      <form class="space-y-4" @submit.prevent="handleLogin">
        <div>
          <label class="block text-xs font-medium text-ink-muted mb-1.5">E-mail Corporativo</label>
          <div class="relative">
            <Mail class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
            <input
              v-model="loginEmail"
              type="email"
              required
              placeholder="seu.email@empresa.com"
              class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-2 text-sm text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-ink-muted mb-1.5">Senha</label>
          <div class="relative">
            <Lock class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
            <input
              v-model="loginPassword"
              type="password"
              required
              placeholder="••••••••"
              class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-2 text-sm text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div v-if="loginError || authError" class="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
          {{ loginError || authError }}
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition flex items-center justify-center space-x-2"
        >
          <span>{{ isLoading ? 'Entrando...' : 'Entrar na Conta' }}</span>
          <ArrowRight class="w-4 h-4" />
        </button>
      </form>

      <!-- Instant 1-Click Demo Profiles -->
      <div class="pt-4 border-t border-hairline space-y-3">
        <div class="flex items-center justify-between text-xs text-ink-subtle">
          <span class="font-medium">Acesso Rápido para Demonstração:</span>
          <span class="text-[11px]">1 clique para testar</span>
        </div>

        <div class="grid grid-cols-2 gap-2.5">
          <!-- Gestor Facilities -->
          <button
            type="button"
            class="flex items-center space-x-2.5 p-2.5 rounded-xl bg-surface-2 hover:bg-surface-3 border border-hairline text-left transition group"
            @click="handleDemoLogin('admin')"
          >
            <img
              src="https://api.dicebear.com/7.x/bottts/svg?seed=Admin"
              alt="Admin"
              class="w-8 h-8 rounded-full border border-purple-500/40 bg-surface-1 shrink-0"
            />
            <div class="min-w-0">
              <p class="text-xs font-bold text-ink truncate group-hover:text-primary transition">Carlos Gestor</p>
              <p class="text-[10px] text-purple-400 font-medium">Facilities Lead (Admin)</p>
            </div>
          </button>

          <!-- Lucas Dev -->
          <button
            type="button"
            class="flex items-center space-x-2.5 p-2.5 rounded-xl bg-surface-2 hover:bg-surface-3 border border-hairline text-left transition group"
            @click="handleDemoLogin('colaborador')"
          >
            <img
              src="https://api.dicebear.com/7.x/bottts/svg?seed=Lucas"
              alt="Lucas"
              class="w-8 h-8 rounded-full border border-emerald-500/40 bg-surface-1 shrink-0"
            />
            <div class="min-w-0">
              <p class="text-xs font-bold text-ink truncate group-hover:text-primary transition">Lucas Dev</p>
              <p class="text-[10px] text-emerald-400 font-medium">Engenharia (Baia A-01)</p>
            </div>
          </button>

          <!-- Mariana Silva -->
          <button
            type="button"
            class="flex items-center space-x-2.5 p-2.5 rounded-xl bg-surface-2 hover:bg-surface-3 border border-hairline text-left transition group"
            @click="handleDemoLogin('mariana')"
          >
            <img
              src="https://api.dicebear.com/7.x/bottts/svg?seed=Mariana"
              alt="Mariana"
              class="w-8 h-8 rounded-full border border-amber-500/40 bg-surface-1 shrink-0"
            />
            <div class="min-w-0">
              <p class="text-xs font-bold text-ink truncate group-hover:text-primary transition">Mariana Silva</p>
              <p class="text-[10px] text-amber-400 font-medium">Product Design (Baia A-02)</p>
            </div>
          </button>

          <!-- Rodrigo Lima -->
          <button
            type="button"
            class="flex items-center space-x-2.5 p-2.5 rounded-xl bg-surface-2 hover:bg-surface-3 border border-hairline text-left transition group"
            @click="handleDemoLogin('rodrigo')"
          >
            <img
              src="https://api.dicebear.com/7.x/bottts/svg?seed=Rodrigo"
              alt="Rodrigo"
              class="w-8 h-8 rounded-full border border-blue-500/40 bg-surface-1 shrink-0"
            />
            <div class="min-w-0">
              <p class="text-xs font-bold text-ink truncate group-hover:text-primary transition">Rodrigo Lima</p>
              <p class="text-[10px] text-blue-400 font-medium">Data Scientist</p>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- TAB 2: REGISTER WITH AVATAR PICKER -->
    <div v-else-if="activeTab === 'register'" class="bg-surface-1 border border-hairline rounded-2xl p-6 shadow-xl space-y-6">
      <form class="space-y-4" @submit.prevent="handleRegister">
        <!-- Name & Email -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1.5">Nome Completo</label>
            <div class="relative">
              <UserIcon class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
              <input
                v-model="regFullName"
                type="text"
                required
                placeholder="Ex: Beatriz Souza"
                class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-2 text-sm text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1.5">E-mail</label>
            <div class="relative">
              <Mail class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
              <input
                v-model="regEmail"
                type="email"
                required
                placeholder="beatriz@empresa.com"
                class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-2 text-sm text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        <!-- Password & Role -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1.5">Senha</label>
            <div class="relative">
              <Lock class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
              <input
                v-model="regPassword"
                type="password"
                required
                placeholder="Mínimo 6 caracteres"
                class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-2 text-sm text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1.5">Perfil de Acesso</label>
            <select
              v-model="regRole"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            >
              <option value="colaborador">Colaborador (Reservas)</option>
              <option value="admin">Gestor (Facilities & Baias)</option>
            </select>
          </div>
        </div>

        <!-- Job & Department -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1.5">Cargo / Especialidade</label>
            <div class="relative">
              <Briefcase class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
              <input
                v-model="regJobTitle"
                type="text"
                placeholder="Ex: Arquiteta de Software"
                class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-2 text-sm text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1.5">Departamento</label>
            <div class="relative">
              <Building class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
              <select
                v-model="regDepartment"
                class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              >
                <option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- AVATAR & PHOTO PICKER -->
        <div class="pt-2 border-t border-hairline space-y-3">
          <label class="block text-xs font-semibold text-ink">Escolha seu Avatar 3D no Mapa</label>
          <div class="flex items-center space-x-4">
            <!-- Active Preview -->
            <div class="relative shrink-0">
              <img
                :src="selectedAvatarPreview"
                alt="Avatar Preview"
                class="w-16 h-16 rounded-full border-2 border-primary bg-surface-2 object-cover shadow-lg"
              />
              <span class="absolute bottom-0 right-0 bg-primary text-white text-[9px] font-bold px-1 rounded-full">
                3D
              </span>
            </div>

            <!-- Avatar Presets -->
            <div class="flex-1">
              <p class="text-[11px] text-ink-subtle mb-1.5">Modelos Digitais Prontos:</p>
              <div class="flex items-center space-x-2">
                <button
                  v-for="preset in avatarPresets"
                  :key="preset.name"
                  type="button"
                  class="w-9 h-9 rounded-full border p-0.5 transition"
                  :class="regAvatarUrl === preset.url && !regCustomPhoto ? 'border-primary ring-2 ring-primary/30 scale-110' : 'border-hairline hover:border-ink-muted'"
                  @click="() => { regAvatarUrl = preset.url; regCustomPhoto = ''; }"
                >
                  <img :src="preset.url" :alt="preset.name" class="w-full h-full rounded-full object-cover" />
                </button>
              </div>
            </div>
          </div>

          <!-- Custom Photo URL -->
          <div>
            <label class="block text-[11px] text-ink-subtle mb-1">Ou use a URL de sua foto real (opcional):</label>
            <div class="relative">
              <ImageIcon class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
              <input
                v-model="regCustomPhoto"
                type="url"
                placeholder="https://images.unsplash.com/photo-..."
                class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-1.5 text-xs text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        <div v-if="regError || authError" class="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
          {{ regError || authError }}
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition flex items-center justify-center space-x-2"
        >
          <span>{{ isLoading ? 'Cadastrando...' : 'Criar Perfil e Entrar' }}</span>
          <ArrowRight class="w-4 h-4" />
        </button>
      </form>
    </div>

    <!-- TAB 3: CURRENT PROFILE -->
    <div v-else-if="activeTab === 'profile' && currentUser" class="bg-surface-1 border border-hairline rounded-2xl p-6 shadow-xl space-y-6">
      <!-- READ VIEW -->
      <template v-if="!isEditingProfile">
        <div class="flex items-center space-x-4">
          <div class="relative">
            <img
              :src="currentUser.photo_url || currentUser.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=User'"
              :alt="currentUser.full_name"
              class="w-20 h-20 rounded-full border-2 border-primary bg-surface-2 object-cover shadow-xl"
            />
            <span class="absolute bottom-0 right-0 bg-emerald-500 w-4 h-4 rounded-full border-2 border-surface-1" />
          </div>

          <div class="space-y-1 flex-1">
            <div class="flex items-center space-x-2">
              <h3 class="text-lg font-bold text-ink">{{ currentUser.full_name }}</h3>
              <span
                class="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider"
                :class="{
                  'bg-purple-500/20 text-purple-400 border border-purple-500/30': currentUser.role === 'admin',
                  'bg-amber-500/20 text-amber-400 border border-amber-500/30': currentUser.role === 'gestor',
                  'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30': currentUser.role === 'colaborador',
                }"
              >
                {{ currentUser.role === 'admin' ? 'Administrador' : (currentUser.role === 'gestor' ? 'Gestor' : 'Colaborador') }}
              </span>
            </div>
            <p class="text-xs text-ink-subtle">{{ currentUser.email }}</p>
            <div class="flex flex-wrap items-center gap-3 text-xs text-ink-muted pt-1">
              <span class="flex items-center space-x-1">
                <Briefcase class="w-3.5 h-3.5 text-primary" />
                <span class="text-ink font-medium">{{ currentUser.job_title || 'Cargo não definido' }}</span>
              </span>
              <span class="flex items-center space-x-1">
                <Building class="w-3.5 h-3.5 text-emerald-400" />
                <span>{{ currentUser.department || 'Geral' }}</span>
              </span>
            </div>
          </div>

          <button
            type="button"
            class="px-3 py-1.5 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold flex items-center space-x-1.5 transition"
            @click="startEditingProfile"
          >
            <Edit3 class="w-3.5 h-3.5 text-primary" />
            <span>Editar Perfil & Cargo</span>
          </button>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-2 gap-3 pt-4 border-t border-hairline">
          <button
            type="button"
            class="flex items-center justify-center space-x-2 py-2.5 px-4 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
            @click="emit('login-success')"
          >
            <span>Ir para Mapa 3D</span>
            <ArrowRight class="w-4 h-4" />
          </button>

          <button
            type="button"
            class="flex items-center justify-center space-x-2 py-2.5 px-4 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
            @click="handleLogout"
          >
            <LogOut class="w-4 h-4 text-red-400" />
            <span>Sair da Conta</span>
          </button>
        </div>
      </template>

      <!-- EDIT VIEW -->
      <form v-else class="space-y-4" @submit.prevent="handleSaveProfile">
        <div class="flex items-center justify-between border-b border-hairline pb-2">
          <div class="flex items-center space-x-2">
            <Edit3 class="w-4 h-4 text-primary" />
            <h3 class="font-bold text-sm text-ink">Editar Informações do Perfil & Cargo</h3>
          </div>
          <button
            type="button"
            class="text-xs text-ink-subtle hover:text-ink"
            @click="isEditingProfile = false"
          >
            Cancelar
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Nome Completo</label>
            <input
              v-model="editFullName"
              type="text"
              required
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Cargo / Função Profissional</label>
            <input
              v-model="editJobTitle"
              type="text"
              required
              placeholder="Ex: Engenheiro de Software Sênior"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-ink-muted mb-1">Departamento</label>
          <select
            v-model="editDepartment"
            class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
          >
            <option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>

        <!-- AVATAR & PHOTO PICKER -->
        <div class="pt-2 border-t border-hairline space-y-3">
          <label class="block text-xs font-semibold text-ink">Avatar 3D na Maquete e Foto</label>
          <div class="flex items-center space-x-4">
            <div class="relative shrink-0">
              <img
                :src="editAvatarPreview"
                alt="Avatar Preview"
                class="w-16 h-16 rounded-full border-2 border-primary bg-surface-2 object-cover shadow-lg"
              />
              <span class="absolute bottom-0 right-0 bg-primary text-white text-[9px] font-bold px-1 rounded-full">
                3D
              </span>
            </div>

            <div class="flex-1">
              <p class="text-[11px] text-ink-subtle mb-1.5">Modelos Digitais Prontos:</p>
              <div class="flex items-center space-x-2">
                <button
                  v-for="preset in avatarPresets"
                  :key="preset.name"
                  type="button"
                  class="w-9 h-9 rounded-full border p-0.5 transition"
                  :class="editAvatarUrl === preset.url && !editCustomPhoto ? 'border-primary ring-2 ring-primary/30 scale-110' : 'border-hairline hover:border-ink-muted'"
                  @click="() => { editAvatarUrl = preset.url; editCustomPhoto = ''; }"
                >
                  <img :src="preset.url" :alt="preset.name" class="w-full h-full rounded-full object-cover" />
                </button>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-[11px] text-ink-subtle mb-1">Ou use a URL de sua foto real (opcional):</label>
            <input
              v-model="editCustomPhoto"
              type="url"
              placeholder="https://images.unsplash.com/photo-..."
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-1.5 text-xs text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-ink-muted mb-1">Nova Senha (deixe em branco para manter a atual)</label>
          <input
            v-model="editPassword"
            type="password"
            placeholder="••••••••"
            class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
          />
        </div>

        <div v-if="editError" class="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
          {{ editError }}
        </div>

        <div v-if="editSuccess" class="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-lg flex items-center space-x-2">
          <Check class="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Perfil e cargo atualizados com sucesso!</span>
        </div>

        <div class="flex items-center space-x-3 pt-2">
          <button
            type="submit"
            :disabled="isSavingProfile"
            class="flex-1 py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            {{ isSavingProfile ? 'Salvando...' : 'Salvar Alterações' }}
          </button>
          <button
            type="button"
            class="px-4 py-2.5 bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold rounded-lg transition"
            @click="isEditingProfile = false"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
