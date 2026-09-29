<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  Users,
  UserPlus,
  Shield,
  Briefcase,
  Building,
  Search,
  Edit3,
  Trash2,
  X,
  RefreshCw,
  AlertTriangle,
  UserCheck,
  Plus,
  CheckCircle2,
} from 'lucide-vue-next';
import { api } from '../services/api';
import { useAuth } from '../stores/auth';
import type { Department, User, UserRole } from '../types';

const { currentUser } = useAuth();

// Sub-Tab Switcher
const currentAdminTab = ref<'users' | 'departments'>('users');

// ==========================================
// USERS STATE & LOGIC
// ==========================================
const users = ref<User[]>([]);
const isLoading = ref(false);
const searchTerm = ref('');
const selectedRoleFilter = ref<string | null>(null);

// Modal states for Users
const showCreateModal = ref(false);
const editingUser = ref<User | null>(null);
const userToDelete = ref<User | null>(null);
const isSaving = ref(false);
const isDeleting = ref(false);
const modalError = ref<string | null>(null);
const deleteError = ref<string | null>(null);

// Create user form
const createForm = ref({
  full_name: '',
  email: '',
  password: '',
  role: 'colaborador' as UserRole,
  job_title: '',
  department: 'Engenharia & Tecnologia',
  avatar_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=NewUser',
});

// Edit user form
const editForm = ref({
  full_name: '',
  email: '',
  role: 'colaborador' as UserRole,
  job_title: '',
  department: 'Engenharia & Tecnologia',
  is_active: true,
  password: '',
});

// ==========================================
// DEPARTMENTS STATE & LOGIC
// ==========================================
const departmentsList = ref<Department[]>([]);
const isDepartmentsLoading = ref(false);
const departmentSearch = ref('');
const showCreateDeptModal = ref(false);
const editingDept = ref<Department | null>(null);
const deptToDelete = ref<Department | null>(null);
const isSavingDept = ref(false);
const isDeletingDept = ref(false);
const deptModalError = ref<string | null>(null);
const deptDeleteError = ref<string | null>(null);

const createDeptForm = ref({
  name: '',
  code: '',
  description: '',
  is_active: true,
});

const editDeptForm = ref({
  name: '',
  code: '',
  description: '',
  is_active: true,
});

// Standard fallback departments
const defaultDepartmentNames = [
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
  if (departmentsList.value.length === 0) {
    return defaultDepartmentNames;
  }
  const fromDb = departmentsList.value.map((d) => d.name);
  const combined = Array.from(new Set([...fromDb, ...defaultDepartmentNames]));
  return combined.sort();
});

const filteredDepartments = computed(() => {
  if (!departmentSearch.value.trim()) return departmentsList.value;
  const term = departmentSearch.value.toLowerCase();
  return departmentsList.value.filter(
    (d) =>
      d.name.toLowerCase().includes(term) ||
      (d.code && d.code.toLowerCase().includes(term)) ||
      (d.description && d.description.toLowerCase().includes(term))
  );
});

const totalDeptMembers = computed(() => {
  return departmentsList.value.reduce((acc, d) => acc + (d.users_count || 0), 0);
});

// User Computeds
const filteredUsers = computed(() => {
  return users.value.filter((u) => {
    if (selectedRoleFilter.value && u.role !== selectedRoleFilter.value) {
      return false;
    }
    if (searchTerm.value.trim()) {
      const term = searchTerm.value.toLowerCase();
      const matchName = u.full_name.toLowerCase().includes(term);
      const matchEmail = u.email.toLowerCase().includes(term);
      const matchJob = u.job_title ? u.job_title.toLowerCase().includes(term) : false;
      const matchDept = u.department ? u.department.toLowerCase().includes(term) : false;
      return matchName || matchEmail || matchJob || matchDept;
    }
    return true;
  });
});

const totalAdmins = computed(() => users.value.filter((u) => u.role === 'admin').length);
const totalGestores = computed(() => users.value.filter((u) => u.role === 'gestor').length);
const totalColaboradores = computed(
  () => users.value.filter((u) => u.role === 'colaborador').length
);

// Loaders
async function loadUsers() {
  isLoading.value = true;
  try {
    users.value = await api.users.list();
  } catch (err: any) {
    alert('Erro ao carregar lista de usuários: ' + (err.message || err));
  } finally {
    isLoading.value = false;
  }
}

async function loadDepartments() {
  isDepartmentsLoading.value = true;
  try {
    departmentsList.value = await api.departments.list();
  } catch (err: any) {
    console.error('Erro ao carregar departamentos:', err);
  } finally {
    isDepartmentsLoading.value = false;
  }
}

async function reloadAll() {
  await Promise.all([loadUsers(), loadDepartments()]);
}

// User Actions
function openCreateModal() {
  modalError.value = null;
  createForm.value = {
    full_name: '',
    email: '',
    password: '',
    role: 'colaborador',
    job_title: '',
    department: departmentOptions.value[0] || 'Engenharia & Tecnologia',
    avatar_url: `https://api.dicebear.com/7.x/bottts/svg?seed=User_${Date.now()}`,
  };
  showCreateModal.value = true;
}

function openEditModal(user: User) {
  modalError.value = null;
  editingUser.value = user;
  editForm.value = {
    full_name: user.full_name,
    email: user.email,
    role: user.role,
    job_title: user.job_title || '',
    department: user.department || departmentOptions.value[0] || 'Engenharia & Tecnologia',
    is_active: user.is_active,
    password: '',
  };
}

async function handleCreateUser() {
  isSaving.value = true;
  modalError.value = null;

  try {
    await api.users.create({
      full_name: createForm.value.full_name,
      email: createForm.value.email,
      password: createForm.value.password,
      role: createForm.value.role,
      job_title: createForm.value.job_title || 'Colaborador',
      department: createForm.value.department,
      avatar_url: createForm.value.avatar_url,
    });
    showCreateModal.value = false;
    await reloadAll();
  } catch (err: any) {
    if (err.code === 'EMAIL_ALREADY_REGISTERED') {
      modalError.value = 'Este e-mail já está cadastrado no sistema.';
    } else {
      modalError.value = err.message || 'Falha ao cadastrar usuário.';
    }
  } finally {
    isSaving.value = false;
  }
}

async function handleUpdateUser() {
  if (!editingUser.value) return;
  isSaving.value = true;
  modalError.value = null;

  try {
    const payload: any = {
      full_name: editForm.value.full_name,
      email: editForm.value.email,
      role: editForm.value.role,
      job_title: editForm.value.job_title,
      department: editForm.value.department,
      is_active: editForm.value.is_active,
    };
    if (editForm.value.password.trim()) {
      payload.password = editForm.value.password.trim();
    }

    await api.users.update(editingUser.value.id, payload);
    editingUser.value = null;
    await reloadAll();
  } catch (err: any) {
    if (err.code === 'EMAIL_ALREADY_REGISTERED') {
      modalError.value = 'Este e-mail já está em uso por outro usuário.';
    } else {
      modalError.value = err.message || 'Falha ao atualizar dados do usuário.';
    }
  } finally {
    isSaving.value = false;
  }
}

async function toggleUserStatus(user: User) {
  if (user.id === currentUser.value?.id) {
    alert('Você não pode desativar sua própria conta de administrador.');
    return;
  }

  try {
    await api.users.update(user.id, {
      is_active: !user.is_active,
    });
    await reloadAll();
  } catch (err: any) {
    alert('Erro ao alterar status do usuário: ' + (err.message || err));
  }
}

function confirmDeleteUser(user: User) {
  deleteError.value = null;
  userToDelete.value = user;
}

async function handleDeleteUser() {
  if (!userToDelete.value) return;
  isDeleting.value = true;
  deleteError.value = null;

  try {
    await api.users.delete(userToDelete.value.id);
    userToDelete.value = null;
    await reloadAll();
  } catch (err: any) {
    if (err.code === 'CANNOT_DELETE_SELF') {
      deleteError.value = 'Você não pode excluir sua própria conta de administrador.';
    } else {
      deleteError.value = err.message || 'Falha ao remover usuário.';
    }
  } finally {
    isDeleting.value = false;
  }
}

// ==========================================
// DEPARTMENT ACTIONS
// ==========================================
function openCreateDeptModal() {
  deptModalError.value = null;
  createDeptForm.value = {
    name: '',
    code: '',
    description: '',
    is_active: true,
  };
  showCreateDeptModal.value = true;
}

function openEditDeptModal(dept: Department) {
  deptModalError.value = null;
  editingDept.value = dept;
  editDeptForm.value = {
    name: dept.name,
    code: dept.code || '',
    description: dept.description || '',
    is_active: dept.is_active,
  };
}

async function handleCreateDept() {
  isSavingDept.value = true;
  deptModalError.value = null;

  try {
    await api.departments.create({
      name: createDeptForm.value.name,
      code: createDeptForm.value.code || null,
      description: createDeptForm.value.description || null,
      is_active: createDeptForm.value.is_active,
    });
    showCreateDeptModal.value = false;
    await loadDepartments();
  } catch (err: any) {
    if (err.code === 'DEPARTMENT_NAME_EXISTS') {
      deptModalError.value = 'Já existe um departamento com este nome.';
    } else {
      deptModalError.value = err.message || 'Falha ao criar departamento.';
    }
  } finally {
    isSavingDept.value = false;
  }
}

async function handleUpdateDept() {
  if (!editingDept.value) return;
  isSavingDept.value = true;
  deptModalError.value = null;

  try {
    await api.departments.update(editingDept.value.id, {
      name: editDeptForm.value.name,
      code: editDeptForm.value.code || null,
      description: editDeptForm.value.description || null,
      is_active: editDeptForm.value.is_active,
    });
    editingDept.value = null;
    await reloadAll();
  } catch (err: any) {
    if (err.code === 'DEPARTMENT_NAME_EXISTS') {
      deptModalError.value = 'Já existe um departamento com este nome.';
    } else {
      deptModalError.value = err.message || 'Falha ao atualizar departamento.';
    }
  } finally {
    isSavingDept.value = false;
  }
}

async function toggleDeptStatus(dept: Department) {
  try {
    await api.departments.update(dept.id, {
      is_active: !dept.is_active,
    });
    await loadDepartments();
  } catch (err: any) {
    alert('Erro ao alterar status do departamento: ' + (err.message || err));
  }
}

function confirmDeleteDept(dept: Department) {
  deptDeleteError.value = null;
  deptToDelete.value = dept;
}

async function handleDeleteDept() {
  if (!deptToDelete.value) return;
  isDeletingDept.value = true;
  deptDeleteError.value = null;

  try {
    await api.departments.delete(deptToDelete.value.id);
    deptToDelete.value = null;
    await loadDepartments();
  } catch (err: any) {
    if (err.code === 'DEPARTMENT_HAS_USERS') {
      deptDeleteError.value = err.message || 'Não é possível excluir departamento com colaboradores associados.';
    } else {
      deptDeleteError.value = err.message || 'Falha ao excluir departamento.';
    }
  } finally {
    isDeletingDept.value = false;
  }
}

onMounted(() => {
  reloadAll();
});
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8 space-y-6">
    <!-- Top Navigation Tabs: Users vs Departments -->
    <div class="flex items-center space-x-2 border-b border-hairline pb-4">
      <button
        class="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition shadow-sm"
        :class="currentAdminTab === 'users' ? 'bg-primary text-white shadow-primary/20' : 'bg-surface-2 hover:bg-surface-3 text-ink-subtle hover:text-ink border border-hairline'"
        @click="currentAdminTab = 'users'"
      >
        <Users class="w-4 h-4" />
        <span>Colaboradores & Cargos ({{ users.length }})</span>
      </button>

      <button
        class="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition shadow-sm"
        :class="currentAdminTab === 'departments' ? 'bg-primary text-white shadow-primary/20' : 'bg-surface-2 hover:bg-surface-3 text-ink-subtle hover:text-ink border border-hairline'"
        @click="currentAdminTab = 'departments'"
      >
        <Building class="w-4 h-4" />
        <span>Departamentos Corporativos ({{ departmentsList.length }})</span>
      </button>
    </div>

    <!-- ============================================================ -->
    <!-- VIEW 1: COLABORADORES & CARGOS -->
    <!-- ============================================================ -->
    <template v-if="currentAdminTab === 'users'">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold text-ink tracking-tight flex items-center space-x-2">
            <Users class="w-5 h-5 text-primary" />
            <span>Gestão de Equipe, Cargos & Níveis de Acesso</span>
          </h2>
          <p class="text-xs text-ink-subtle mt-1">
            Defina atribuições corporativas, promova colaboradores a gestores e edite cargos (job titles) e departamentos.
          </p>
        </div>

        <div class="flex items-center space-x-2.5">
          <button
            class="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
            @click="reloadAll"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
            <span>Atualizar</span>
          </button>

          <button
            class="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
            @click="openCreateModal"
          >
            <UserPlus class="w-4 h-4" />
            <span>+ Novo Colaborador</span>
          </button>
        </div>
      </div>

      <!-- Metrics Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-surface-1 border border-hairline rounded-xl p-4 shadow-md flex items-center space-x-3.5">
          <div class="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
            <Users class="w-5 h-5" />
          </div>
          <div>
            <p class="text-[11px] text-ink-subtle uppercase tracking-wider font-semibold">Total de Membros</p>
            <p class="text-xl font-black text-ink">{{ users.length }}</p>
          </div>
        </div>

        <div class="bg-surface-1 border border-hairline rounded-xl p-4 shadow-md flex items-center space-x-3.5">
          <div class="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Shield class="w-5 h-5" />
          </div>
          <div>
            <p class="text-[11px] text-ink-subtle uppercase tracking-wider font-semibold">Gestores & Admins</p>
            <p class="text-xl font-black text-ink">{{ totalAdmins + totalGestores }}</p>
          </div>
        </div>

        <div class="bg-surface-1 border border-hairline rounded-xl p-4 shadow-md flex items-center space-x-3.5">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <UserCheck class="w-5 h-5" />
          </div>
          <div>
            <p class="text-[11px] text-ink-subtle uppercase tracking-wider font-semibold">Colaboradores</p>
            <p class="text-xl font-black text-ink">{{ totalColaboradores }}</p>
          </div>
        </div>
      </div>

      <!-- Search & Role Filters Bar -->
      <div class="bg-surface-1 border border-hairline rounded-xl p-3 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-3">
        <!-- Search Input -->
        <div class="relative flex-1 max-w-md">
          <Search class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Buscar por nome, e-mail, cargo ou departamento..."
            class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-1.5 text-xs text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
          />
        </div>

        <!-- Role Tabs -->
        <div class="flex items-center space-x-1 bg-surface-2 p-1 rounded-lg border border-hairline overflow-x-auto">
          <button
            type="button"
            class="px-3 py-1 text-xs font-semibold rounded-md transition whitespace-nowrap"
            :class="selectedRoleFilter === null ? 'bg-primary text-white shadow-sm' : 'text-ink-subtle hover:text-ink'"
            @click="selectedRoleFilter = null"
          >
            Todos ({{ users.length }})
          </button>
          <button
            type="button"
            class="px-3 py-1 text-xs font-semibold rounded-md transition whitespace-nowrap"
            :class="selectedRoleFilter === 'admin' ? 'bg-purple-600 text-white shadow-sm' : 'text-ink-subtle hover:text-ink'"
            @click="selectedRoleFilter = 'admin'"
          >
            👑 Admins ({{ totalAdmins }})
          </button>
          <button
            type="button"
            class="px-3 py-1 text-xs font-semibold rounded-md transition whitespace-nowrap"
            :class="selectedRoleFilter === 'gestor' ? 'bg-amber-600 text-white shadow-sm' : 'text-ink-subtle hover:text-ink'"
            @click="selectedRoleFilter = 'gestor'"
          >
            🛡️ Gestores ({{ totalGestores }})
          </button>
          <button
            type="button"
            class="px-3 py-1 text-xs font-semibold rounded-md transition whitespace-nowrap"
            :class="selectedRoleFilter === 'colaborador' ? 'bg-emerald-600 text-white shadow-sm' : 'text-ink-subtle hover:text-ink'"
            @click="selectedRoleFilter = 'colaborador'"
          >
            👤 Colaboradores ({{ totalColaboradores }})
          </button>
        </div>
      </div>

      <!-- Users Table -->
      <div class="bg-surface-1 border border-hairline rounded-xl shadow-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-surface-2/60 text-ink-subtle font-semibold border-b border-hairline">
              <tr>
                <th class="py-3 px-4">Colaborador</th>
                <th class="py-3 px-4">Cargo / Função</th>
                <th class="py-3 px-4">Departamento</th>
                <th class="py-3 px-4">Papel & Nível de Acesso</th>
                <th class="py-3 px-4 text-center">Status</th>
                <th class="py-3 px-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-hairline">
              <tr
                v-for="u in filteredUsers"
                :key="u.id"
                class="hover:bg-surface-2/40 transition group"
                :class="{ 'opacity-60 bg-surface-2/10': !u.is_active }"
              >
                <!-- Colaborador -->
                <td class="py-3.5 px-4">
                  <div class="flex items-center space-x-3">
                    <img
                      :src="u.photo_url || u.avatar_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=User'"
                      :alt="u.full_name"
                      class="w-8 h-8 rounded-full border border-hairline bg-surface-2 object-cover shrink-0"
                    />
                    <div>
                      <p class="font-bold text-ink flex items-center space-x-1.5">
                        <span>{{ u.full_name }}</span>
                        <span v-if="u.id === currentUser?.id" class="text-[9px] bg-primary/20 text-primary px-1.5 py-0.2 rounded font-semibold">
                          Você
                        </span>
                      </p>
                      <p class="text-[11px] text-ink-subtle">{{ u.email }}</p>
                    </div>
                  </div>
                </td>

                <!-- Cargo -->
                <td class="py-3.5 px-4 font-medium text-ink">
                  <span class="flex items-center space-x-1.5">
                    <Briefcase class="w-3.5 h-3.5 text-primary shrink-0" />
                    <span>{{ u.job_title || 'Não informado' }}</span>
                  </span>
                </td>

                <!-- Departamento -->
                <td class="py-3.5 px-4 text-ink-muted">
                  <span class="flex items-center space-x-1.5">
                    <Building class="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>{{ u.department || 'Geral' }}</span>
                  </span>
                </td>

                <!-- Role Badge -->
                <td class="py-3.5 px-4">
                  <span
                    class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider inline-flex items-center space-x-1"
                    :class="{
                      'bg-purple-500/20 text-purple-400 border border-purple-500/30': u.role === 'admin',
                      'bg-amber-500/20 text-amber-400 border border-amber-500/30': u.role === 'gestor',
                      'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30': u.role === 'colaborador',
                    }"
                  >
                    <span>{{ u.role === 'admin' ? '👑 Administrador' : (u.role === 'gestor' ? '🛡️ Gestor' : '👤 Colaborador') }}</span>
                  </span>
                </td>

                <!-- Status -->
                <td class="py-3.5 px-4 text-center">
                  <button
                    type="button"
                    class="px-2 py-0.5 rounded text-[10px] font-semibold transition"
                    :class="u.is_active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20'"
                    :title="u.is_active ? 'Clique para desativar conta' : 'Clique para reativar conta'"
                    @click="toggleUserStatus(u)"
                  >
                    {{ u.is_active ? 'Ativa' : 'Inativa' }}
                  </button>
                </td>

                <!-- Ações -->
                <td class="py-3.5 px-4 text-right">
                  <div class="flex items-center justify-end space-x-1.5">
                    <button
                      class="p-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink hover:text-primary transition"
                      title="Editar Cargo e Papel"
                      @click="openEditModal(u)"
                    >
                      <Edit3 class="w-3.5 h-3.5" />
                    </button>

                    <button
                      v-if="u.id !== currentUser?.id"
                      class="p-1.5 rounded-md bg-surface-2 hover:bg-red-500/20 border border-hairline text-ink-subtle hover:text-red-400 transition"
                      title="Excluir Colaborador"
                      @click="confirmDeleteUser(u)"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- ============================================================ -->
    <!-- VIEW 2: DEPARTAMENTOS CORPORATIVOS -->
    <!-- ============================================================ -->
    <template v-else-if="currentAdminTab === 'departments'">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold text-ink tracking-tight flex items-center space-x-2">
            <Building class="w-5 h-5 text-emerald-400" />
            <span>Gestão de Departamentos Corporativos</span>
          </h2>
          <p class="text-xs text-ink-subtle mt-1">
            Cadastre, edite e organize os departamentos da empresa para padronizar perfis, relatórios e alocações de baias.
          </p>
        </div>

        <div class="flex items-center space-x-2.5">
          <button
            class="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
            @click="loadDepartments"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isDepartmentsLoading }" />
            <span>Atualizar</span>
          </button>

          <button
            class="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
            @click="openCreateDeptModal"
          >
            <Plus class="w-4 h-4" />
            <span>+ Novo Departamento</span>
          </button>
        </div>
      </div>

      <!-- Metrics Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-surface-1 border border-hairline rounded-xl p-4 shadow-md flex items-center space-x-3.5">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Building class="w-5 h-5" />
          </div>
          <div>
            <p class="text-[11px] text-ink-subtle uppercase tracking-wider font-semibold">Total de Departamentos</p>
            <p class="text-xl font-black text-ink">{{ departmentsList.length }}</p>
          </div>
        </div>

        <div class="bg-surface-1 border border-hairline rounded-xl p-4 shadow-md flex items-center space-x-3.5">
          <div class="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <p class="text-[11px] text-ink-subtle uppercase tracking-wider font-semibold">Departamentos Ativos</p>
            <p class="text-xl font-black text-ink">{{ departmentsList.filter(d => d.is_active).length }}</p>
          </div>
        </div>

        <div class="bg-surface-1 border border-hairline rounded-xl p-4 shadow-md flex items-center space-x-3.5">
          <div class="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Users class="w-5 h-5" />
          </div>
          <div>
            <p class="text-[11px] text-ink-subtle uppercase tracking-wider font-semibold">Colaboradores Alocados</p>
            <p class="text-xl font-black text-ink">{{ totalDeptMembers }}</p>
          </div>
        </div>
      </div>

      <!-- Search Bar -->
      <div class="bg-surface-1 border border-hairline rounded-xl p-3 shadow-md flex items-center justify-between">
        <div class="relative flex-1 max-w-md">
          <Search class="w-4 h-4 text-ink-subtle absolute left-3 top-2.5" />
          <input
            v-model="departmentSearch"
            type="text"
            placeholder="Buscar por nome, sigla ou descrição do departamento..."
            class="w-full bg-surface-2 border border-hairline rounded-lg pl-9 pr-3 py-1.5 text-xs text-ink placeholder:text-ink-subtle/50 focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      <!-- Departments Table -->
      <div class="bg-surface-1 border border-hairline rounded-xl shadow-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-surface-2/60 text-ink-subtle font-semibold border-b border-hairline">
              <tr>
                <th class="py-3 px-4">Nome do Departamento</th>
                <th class="py-3 px-4">Sigla / Código</th>
                <th class="py-3 px-4">Descrição</th>
                <th class="py-3 px-4 text-center">Membros</th>
                <th class="py-3 px-4 text-center">Status</th>
                <th class="py-3 px-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-hairline">
              <tr v-if="filteredDepartments.length === 0" class="text-center py-8">
                <td colspan="6" class="py-8 text-ink-subtle text-center">
                  Nenhum departamento cadastrado ou correspondente à busca.
                </td>
              </tr>
              <tr
                v-for="d in filteredDepartments"
                :key="d.id"
                class="hover:bg-surface-2/40 transition group"
                :class="{ 'opacity-60 bg-surface-2/10': !d.is_active }"
              >
                <!-- Nome -->
                <td class="py-3.5 px-4 font-bold text-ink">
                  <div class="flex items-center space-x-2">
                    <Building class="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{{ d.name }}</span>
                  </div>
                </td>

                <!-- Sigla / Código -->
                <td class="py-3.5 px-4">
                  <span
                    v-if="d.code"
                    class="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-surface-2 border border-hairline text-primary"
                  >
                    {{ d.code }}
                  </span>
                  <span v-else class="text-ink-subtle text-[11px]">—</span>
                </td>

                <!-- Descrição -->
                <td class="py-3.5 px-4 text-ink-subtle max-w-xs truncate">
                  {{ d.description || 'Sem descrição cadastrada.' }}
                </td>

                <!-- Membros vinculados -->
                <td class="py-3.5 px-4 text-center">
                  <span
                    class="px-2.5 py-0.5 rounded-full text-[10px] font-bold"
                    :class="(d.users_count || 0) > 0 ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-surface-2 text-ink-subtle border border-hairline'"
                  >
                    {{ d.users_count || 0 }} colaborador(es)
                  </span>
                </td>

                <!-- Status -->
                <td class="py-3.5 px-4 text-center">
                  <button
                    type="button"
                    class="px-2 py-0.5 rounded text-[10px] font-semibold transition"
                    :class="d.is_active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20'"
                    :title="d.is_active ? 'Clique para desativar' : 'Clique para ativar'"
                    @click="toggleDeptStatus(d)"
                  >
                    {{ d.is_active ? 'Ativo' : 'Inativo' }}
                  </button>
                </td>

                <!-- Ações -->
                <td class="py-3.5 px-4 text-right">
                  <div class="flex items-center justify-end space-x-1.5">
                    <button
                      class="p-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink hover:text-primary transition"
                      title="Editar Departamento"
                      @click="openEditDeptModal(d)"
                    >
                      <Edit3 class="w-3.5 h-3.5" />
                    </button>

                    <button
                      class="p-1.5 rounded-md bg-surface-2 hover:bg-red-500/20 border border-hairline text-ink-subtle hover:text-red-400 transition"
                      title="Excluir Departamento"
                      @click="confirmDeleteDept(d)"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- ============================================================ -->
    <!-- MODAL: CRIAR COLABORADOR -->
    <!-- ============================================================ -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-4 my-8">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <UserPlus class="w-5 h-5 text-primary" />
            <h3 class="font-bold text-ink text-sm">Cadastrar Novo Colaborador</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="showCreateModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleCreateUser">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Nome Completo *</label>
              <input
                v-model="createForm.full_name"
                type="text"
                required
                placeholder="Ex: Beatriz Mendes"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">E-mail Corporativo *</label>
              <input
                v-model="createForm.email"
                type="email"
                required
                placeholder="beatriz@empresa.com"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Senha Inicial *</label>
              <input
                v-model="createForm.password"
                type="password"
                required
                minlength="4"
                placeholder="Mínimo 4 caracteres"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Cargo (Job Title)</label>
              <input
                v-model="createForm.job_title"
                type="text"
                placeholder="Ex: Desenvolvedor Fullstack"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Departamento</label>
              <select
                v-model="createForm.department"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              >
                <option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Papel & Nível de Acesso *</label>
              <select
                v-model="createForm.role"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary font-bold"
              >
                <option value="colaborador">👤 Colaborador (Agendar e Check-in)</option>
                <option value="gestor">🛡️ Gestor (Gestão de Baias & Salas)</option>
                <option value="admin">👑 Administrador (Acesso Irrestrito)</option>
              </select>
            </div>
          </div>

          <div
            v-if="modalError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ modalError }}</span>
          </div>

          <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
            <button
              type="button"
              class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
              @click="showCreateModal = false"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="isSaving"
              class="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            >
              <RefreshCw v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
              <span>{{ isSaving ? 'Cadastrando...' : 'Cadastrar Membro' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: EDITAR CARGO E PAPEL DO COLABORADOR -->
    <!-- ============================================================ -->
    <div
      v-if="editingUser"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-4 my-8">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Edit3 class="w-5 h-5 text-primary" />
            <h3 class="font-bold text-ink text-sm">Editar Cargo e Permissões</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="editingUser = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleUpdateUser">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Nome Completo</label>
              <input
                v-model="editForm.full_name"
                type="text"
                required
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">E-mail Corporativo</label>
              <input
                v-model="editForm.email"
                type="email"
                required
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Cargo (Job Title)</label>
              <input
                v-model="editForm.job_title"
                type="text"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Departamento</label>
              <select
                v-model="editForm.department"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
              >
                <option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink-muted mb-1">Papel & Nível de Acesso (RBAC)</label>
            <select
              v-model="editForm.role"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary font-bold"
            >
              <option value="colaborador">👤 Colaborador (Reservas Pessoais e Check-in)</option>
              <option value="gestor">🛡️ Gestor (Gestão de Salas, Baias e Plantas)</option>
              <option value="admin">👑 Administrador (Governança Completa e Controle de Equipe)</option>
            </select>
          </div>

          <div class="flex items-center space-x-2 pt-1">
            <input
              id="edit-is-active"
              v-model="editForm.is_active"
              type="checkbox"
              class="rounded bg-surface-2 border-hairline text-primary focus:ring-0 w-4 h-4 cursor-pointer"
            />
            <label for="edit-is-active" class="text-xs text-ink cursor-pointer font-medium">
              Conta Ativa (Permite login e agendamentos no sistema)
            </label>
          </div>

          <div
            v-if="modalError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ modalError }}</span>
          </div>

          <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
            <button
              type="button"
              class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
              @click="editingUser = null"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="isSaving"
              class="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            >
              <RefreshCw v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
              <span>{{ isSaving ? 'Salvando...' : 'Salvar Alterações' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: CONFIRMAR EXCLUSÃO DE USUÁRIO -->
    <!-- ============================================================ -->
    <div
      v-if="userToDelete"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Trash2 class="w-5 h-5 text-red-400" />
            <h3 class="font-bold text-ink text-sm">Confirmar Exclusão de Membro</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="userToDelete = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-3">
          <p class="text-xs text-ink-muted">
            Tem certeza que deseja remover o usuário <strong class="text-ink text-sm">{{ userToDelete.full_name }}</strong> ({{ userToDelete.email }}) do sistema?
          </p>

          <div
            v-if="deleteError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ deleteError }}</span>
          </div>
        </div>

        <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
            @click="userToDelete = null"
          >
            Cancelar
          </button>
          <button
            type="button"
            :disabled="isDeleting"
            class="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            @click="handleDeleteUser"
          >
            <Trash2 class="w-3.5 h-3.5" />
            <span>{{ isDeleting ? 'Removendo...' : 'Sim, Excluir Membro' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: CRIAR DEPARTAMENTO -->
    <!-- ============================================================ -->
    <div
      v-if="showCreateDeptModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4 my-8">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Building class="w-5 h-5 text-emerald-400" />
            <h3 class="font-bold text-ink text-sm">Cadastrar Novo Departamento</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="showCreateDeptModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleCreateDept">
          <div>
            <label class="block text-xs font-semibold text-ink-muted mb-1">Nome do Departamento *</label>
            <input
              v-model="createDeptForm.name"
              type="text"
              required
              placeholder="Ex: Engenharia de Software"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Sigla / Código</label>
              <input
                v-model="createDeptForm.code"
                type="text"
                placeholder="Ex: ENG"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink uppercase focus:outline-none focus:border-primary"
              />
            </div>

            <div class="flex items-center pt-5">
              <label class="flex items-center space-x-2 text-xs text-ink cursor-pointer">
                <input
                  v-model="createDeptForm.is_active"
                  type="checkbox"
                  class="rounded bg-surface-2 border-hairline text-primary focus:ring-0 w-4 h-4 cursor-pointer"
                />
                <span class="font-medium">Ativo</span>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink-muted mb-1">Descrição</label>
            <textarea
              v-model="createDeptForm.description"
              rows="2"
              placeholder="Atividades e escopo do departamento..."
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary resize-none"
            />
          </div>

          <div
            v-if="deptModalError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ deptModalError }}</span>
          </div>

          <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
            <button
              type="button"
              class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
              @click="showCreateDeptModal = false"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="isSavingDept"
              class="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            >
              <RefreshCw v-if="isSavingDept" class="w-3.5 h-3.5 animate-spin" />
              <span>{{ isSavingDept ? 'Salvando...' : 'Criar Departamento' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: EDITAR DEPARTAMENTO -->
    <!-- ============================================================ -->
    <div
      v-if="editingDept"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4 my-8">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Edit3 class="w-5 h-5 text-emerald-400" />
            <h3 class="font-bold text-ink text-sm">Editar Departamento</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="editingDept = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleUpdateDept">
          <div>
            <label class="block text-xs font-semibold text-ink-muted mb-1">Nome do Departamento *</label>
            <input
              v-model="editDeptForm.name"
              type="text"
              required
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-ink-muted mb-1">Sigla / Código</label>
              <input
                v-model="editDeptForm.code"
                type="text"
                placeholder="Ex: ENG"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink uppercase focus:outline-none focus:border-primary"
              />
            </div>

            <div class="flex items-center pt-5">
              <label class="flex items-center space-x-2 text-xs text-ink cursor-pointer">
                <input
                  v-model="editDeptForm.is_active"
                  type="checkbox"
                  class="rounded bg-surface-2 border-hairline text-primary focus:ring-0 w-4 h-4 cursor-pointer"
                />
                <span class="font-medium">Ativo</span>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-ink-muted mb-1">Descrição</label>
            <textarea
              v-model="editDeptForm.description"
              rows="2"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary resize-none"
            />
          </div>

          <div
            v-if="deptModalError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ deptModalError }}</span>
          </div>

          <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
            <button
              type="button"
              class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
              @click="editingDept = null"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="isSavingDept"
              class="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            >
              <RefreshCw v-if="isSavingDept" class="w-3.5 h-3.5 animate-spin" />
              <span>{{ isSavingDept ? 'Salvando...' : 'Salvar Alterações' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: CONFIRMAR EXCLUSÃO DE DEPARTAMENTO -->
    <!-- ============================================================ -->
    <div
      v-if="deptToDelete"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Trash2 class="w-5 h-5 text-red-400" />
            <h3 class="font-bold text-ink text-sm">Confirmar Exclusão de Departamento</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="deptToDelete = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-3">
          <p class="text-xs text-ink-muted">
            Tem certeza que deseja excluir o departamento <strong class="text-ink text-sm">{{ deptToDelete.name }}</strong>?
          </p>

          <div
            v-if="(deptToDelete.users_count || 0) > 0"
            class="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-300 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <span>
              Atenção: Este departamento possui <strong>{{ deptToDelete.users_count }} colaborador(es)</strong> associado(s).
              O sistema impedirá a exclusão até que todos os colaboradores sejam remanejados.
            </span>
          </div>

          <div
            v-if="deptDeleteError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ deptDeleteError }}</span>
          </div>
        </div>

        <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
            @click="deptToDelete = null"
          >
            Cancelar
          </button>
          <button
            type="button"
            :disabled="isDeletingDept"
            class="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            @click="handleDeleteDept"
          >
            <Trash2 class="w-3.5 h-3.5" />
            <span>{{ isDeletingDept ? 'Excluindo...' : 'Sim, Excluir Departamento' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
