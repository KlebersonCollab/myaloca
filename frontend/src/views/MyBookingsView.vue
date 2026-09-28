<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Calendar, Clock, QrCode, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-vue-next';
import { api } from '../services/api';
import type { Booking } from '../types';

const emit = defineEmits<{
  (e: 'open-qr-scanner'): void;
}>();

const bookings = ref<Booking[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

async function loadMyBookings() {
  isLoading.value = true;
  error.value = null;
  try {
    bookings.value = await api.bookings.listMy();
  } catch (err: any) {
    error.value = err.message || 'Falha ao carregar suas reservas.';
  } finally {
    isLoading.value = false;
  }
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function formatTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

onMounted(() => {
  loadMyBookings();
});
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-8 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-ink tracking-tight flex items-center space-x-2">
          <Calendar class="w-5 h-5 text-emerald-400" />
          <span>Minhas Reservas de Baia</span>
        </h2>
        <p class="text-xs text-ink-subtle mt-1">
          Acompanhe suas reservas, faça check-in presencial e gerencie sua escala híbrida.
        </p>
      </div>
      <button
        class="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
        :class="{ 'opacity-50 pointer-events-none': isLoading }"
        @click="loadMyBookings"
      >
        <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
        <span>Atualizar</span>
      </button>
    </div>

    <!-- Loading / Error -->
    <div v-if="isLoading && bookings.length === 0" class="py-12 text-center text-ink-subtle text-sm">
      Carregando histórico de reservas...
    </div>
    <div v-if="error" class="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div
      v-if="!isLoading && bookings.length === 0 && !error"
      class="text-center py-16 bg-surface-1 border border-hairline rounded-xl p-8 space-y-3"
    >
      <div class="w-12 h-12 rounded-full bg-surface-2 flex items-center justify-center mx-auto text-ink-subtle">
        <Calendar class="w-6 h-6" />
      </div>
      <h3 class="text-base font-semibold text-ink">Nenhuma reserva ativa</h3>
      <p class="text-xs text-ink-subtle max-w-sm mx-auto">
        Você ainda não agendou nenhuma baia de trabalho. Vá até o Mapa 3D para escolher seu assento favorito!
      </p>
    </div>

    <!-- Booking List Cards -->
    <div v-if="bookings.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="b in bookings"
        :key="b.id"
        class="bg-surface-1 border border-hairline hover:border-hairline-strong rounded-xl p-5 shadow-lg space-y-4 transition"
      >
        <!-- Top bar: Baia ID and Status Badge -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="text-sm font-bold text-ink">Baia #{{ b.desk_id }}</span>
            <span class="text-xs text-ink-subtle">• {{ formatDate(b.start_time) }}</span>
          </div>

          <span
            class="px-2 py-0.5 text-[10px] font-semibold rounded uppercase"
            :class="{
              'bg-amber-500/10 text-amber-400 border border-amber-500/20':
                b.status === 'PENDENTE_CHECKIN',
              'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20':
                b.status === 'CHECKED_IN',
              'bg-red-500/10 text-red-400 border border-red-500/20':
                b.status === 'EXPIRADA_NO_SHOW' || b.status === 'CANCELADA_USUARIO',
              'bg-hairline text-ink-subtle': b.status === 'FINALIZADA',
            }"
          >
            {{ b.status.replace('_', ' ') }}
          </span>
        </div>

        <!-- Time & Check-in Deadline Info -->
        <div class="space-y-1.5 text-xs text-ink-muted bg-surface-2/60 p-3 rounded-lg border border-hairline">
          <div class="flex items-center justify-between">
            <span class="flex items-center space-x-1.5">
              <Clock class="w-3.5 h-3.5 text-primary" />
              <span>Horário Reservado:</span>
            </span>
            <span class="font-medium text-ink">
              {{ formatTime(b.start_time) }} às {{ formatTime(b.end_time) }}
            </span>
          </div>

          <div
            v-if="b.status === 'PENDENTE_CHECKIN'"
            class="flex items-center justify-between pt-1 border-t border-hairline text-amber-300"
          >
            <span class="flex items-center space-x-1">
              <AlertCircle class="w-3.5 h-3.5" />
              <span>Limite Check-in:</span>
            </span>
            <span class="font-bold">
              {{ formatTime(b.checkin_deadline) }} (Tolerância +30 min)
            </span>
          </div>

          <div
            v-if="b.status === 'CHECKED_IN' && b.checked_in_at"
            class="flex items-center justify-between pt-1 border-t border-hairline text-emerald-400"
          >
            <span class="flex items-center space-x-1">
              <CheckCircle2 class="w-3.5 h-3.5" />
              <span>Presença Confirmada às:</span>
            </span>
            <span>{{ formatTime(b.checked_in_at) }}</span>
          </div>
        </div>

        <!-- Action: Check-in button -->
        <div v-if="b.status === 'PENDENTE_CHECKIN'" class="pt-1">
          <button
            class="w-full py-2 px-3 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center justify-center space-x-2 transition shadow-sm"
            @click="emit('open-qr-scanner')"
          >
            <QrCode class="w-4 h-4" />
            <span>Fazer Check-in Presencial com QR Code</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
