<script setup lang="ts">
import { computed } from 'vue';
import {
  Box,
  Calendar,
  QrCode,
  Shield,
  User as UserIcon,
  LogOut,
  RefreshCw,
} from 'lucide-vue-next';
import { useAuth } from '../stores/auth';

const props = defineProps<{
  currentTab: '3d-office' | 'my-bookings' | 'admin-desks';
}>();

const emit = defineEmits<{
  (e: 'navigate', tab: '3d-office' | 'my-bookings' | 'admin-desks'): void;
  (e: 'open-qr-scanner'): void;
}>();

const { currentUser, isAdmin, switchDemoUser, logout } = useAuth();

const currentRoleLabel = computed(() => {
  if (currentUser.value?.role === 'admin' || currentUser.value?.role === 'gestor') {
    return 'Gestor / Facilities';
  }
  return 'Colaborador';
});

async function handleSwitchRole() {
  if (isAdmin.value) {
    await switchDemoUser('colaborador');
  } else {
    await switchDemoUser('admin');
  }
}
</script>

<template>
  <header class="border-b border-hairline bg-surface-1/90 backdrop-blur sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <!-- Brand & Title -->
      <div class="flex items-center space-x-6">
        <div class="flex items-center space-x-3 cursor-pointer" @click="emit('navigate', '3d-office')">
          <div class="w-9 h-9 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center text-primary shadow-sm shadow-primary/20">
            <Box class="w-5 h-5" />
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-bold tracking-tight text-ink text-base">MyAloca</span>
              <span class="px-1.5 py-0.5 text-[10px] uppercase font-semibold bg-surface-3 text-ink-subtle rounded border border-hairline">
                3D Hybrid
              </span>
            </div>
            <p class="text-xs text-ink-subtle">Gestão de Baias & Presença</p>
          </div>
        </div>

        <!-- Navigation tabs -->
        <nav class="hidden md:flex items-center space-x-1">
          <button
            class="px-3 py-1.5 rounded-md text-sm font-medium transition flex items-center space-x-2"
            :class="
              props.currentTab === '3d-office'
                ? 'bg-surface-3 text-ink border border-hairline-strong shadow-sm'
                : 'text-ink-subtle hover:text-ink hover:bg-surface-2'
            "
            @click="emit('navigate', '3d-office')"
          >
            <Box class="w-4 h-4 text-primary" />
            <span>Mapa 3D</span>
          </button>

          <button
            class="px-3 py-1.5 rounded-md text-sm font-medium transition flex items-center space-x-2"
            :class="
              props.currentTab === 'my-bookings'
                ? 'bg-surface-3 text-ink border border-hairline-strong shadow-sm'
                : 'text-ink-subtle hover:text-ink hover:bg-surface-2'
            "
            @click="emit('navigate', 'my-bookings')"
          >
            <Calendar class="w-4 h-4 text-emerald-400" />
            <span>Minhas Reservas</span>
          </button>

          <button
            v-if="isAdmin"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition flex items-center space-x-2"
            :class="
              props.currentTab === 'admin-desks'
                ? 'bg-surface-3 text-ink border border-hairline-strong shadow-sm'
                : 'text-ink-subtle hover:text-ink hover:bg-surface-2'
            "
            @click="emit('navigate', 'admin-desks')"
          >
            <Shield class="w-4 h-4 text-purple-400" />
            <span>Painel do Gestor</span>
          </button>
        </nav>
      </div>

      <!-- Quick Actions & User Profile -->
      <div class="flex items-center space-x-3">
        <!-- Check-in QR Scanner Button -->
        <button
          class="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition active:scale-95"
          @click="emit('open-qr-scanner')"
          title="Fazer Check-in Presencial"
        >
          <QrCode class="w-4 h-4" />
          <span class="hidden sm:inline">Check-in QR</span>
        </button>

        <!-- Demo Role Switcher -->
        <button
          class="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink-muted text-xs transition"
          @click="handleSwitchRole"
          :title="`Trocar para perfil de ${isAdmin ? 'Colaborador' : 'Gestor'}`"
        >
          <RefreshCw class="w-3.5 h-3.5 text-primary" />
          <span class="hidden lg:inline">Alternar:</span>
          <span class="font-medium text-ink">{{ isAdmin ? 'Gestor' : 'Colaborador' }}</span>
        </button>

        <!-- Current User Avatar / Badge -->
        <div class="flex items-center space-x-2.5 pl-2 border-l border-hairline">
          <div class="w-8 h-8 rounded-full bg-surface-3 border border-hairline flex items-center justify-center overflow-hidden">
            <img
              v-if="currentUser?.avatar_url || currentUser?.photo_url"
              :src="currentUser.avatar_url || currentUser.photo_url || ''"
              :alt="currentUser.full_name"
              class="w-full h-full object-cover"
            />
            <UserIcon v-else class="w-4 h-4 text-ink-subtle" />
          </div>
          <div class="hidden sm:block text-left">
            <div class="text-xs font-medium text-ink leading-tight">
              {{ currentUser?.full_name || 'Carregando...' }}
            </div>
            <div class="text-[10px] text-ink-subtle">
              {{ currentRoleLabel }}
            </div>
          </div>
          <button
            class="p-1 rounded text-ink-subtle hover:text-ink hover:bg-surface-2 transition"
            title="Sair"
            @click="logout"
          >
            <LogOut class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
