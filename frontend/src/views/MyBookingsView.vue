<script setup lang="ts">
import { onMounted, ref } from 'vue';
import {
  Calendar,
  Clock,
  QrCode,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  LogOut,
  XCircle,
  AlertTriangle,
} from 'lucide-vue-next';
import { api } from '../services/api';
import type { Booking } from '../types';

const emit = defineEmits<{
  (e: 'open-qr-scanner'): void;
  (e: 'booking-updated'): void;
}>();

const bookings = ref<Booking[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);
const successMessage = ref<string | null>(null);

// Confirmation Modal State
const confirmModalOpen = ref(false);
const confirmActionType = ref<'cancel' | 'checkout'>('cancel');
const targetBooking = ref<Booking | null>(null);
const isProcessingAction = ref(false);

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

function promptCancel(booking: Booking) {
  targetBooking.value = booking;
  confirmActionType.value = 'cancel';
  confirmModalOpen.value = true;
}

function promptCheckout(booking: Booking) {
  targetBooking.value = booking;
  confirmActionType.value = 'checkout';
  confirmModalOpen.value = true;
}

async function executeAction() {
  if (!targetBooking.value) return;
  isProcessingAction.value = true;
  error.value = null;
  successMessage.value = null;

  try {
    if (confirmActionType.value === 'cancel') {
      await api.bookings.cancel(targetBooking.value.id);
      successMessage.value = `Reserva #${targetBooking.value.id} cancelada com sucesso.`;
    } else {
      await api.bookings.checkout(targetBooking.value.id);
      successMessage.value = `Baia #${targetBooking.value.desk_id} liberada com sucesso! O assento já está disponível para seus colegas.`;
    }
    confirmModalOpen.value = false;
    targetBooking.value = null;
    await loadMyBookings();
    emit('booking-updated');
  } catch (err: any) {
    error.value = err.message || 'Falha ao processar solicitação.';
  } finally {
    isProcessingAction.value = false;
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

    <!-- Feedback messages -->
    <div v-if="successMessage" class="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-400 flex items-center justify-between">
      <span>{{ successMessage }}</span>
      <button class="text-emerald-400/80 hover:text-emerald-400 text-xs" @click="successMessage = null">✕</button>
    </div>
    <div v-if="error" class="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400 flex items-center justify-between">
      <span>{{ error }}</span>
      <button class="text-red-400/80 hover:text-red-400 text-xs" @click="error = null">✕</button>
    </div>

    <!-- Loading / Error -->
    <div v-if="isLoading && bookings.length === 0" class="py-12 text-center text-ink-subtle text-sm">
      Carregando histórico de reservas...
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

        <!-- Actions -->
        <div class="space-y-2 pt-1">
          <!-- Pending: Check-in button and Cancel button -->
          <div v-if="b.status === 'PENDENTE_CHECKIN'" class="flex flex-col sm:flex-row gap-2">
            <button
              class="flex-1 py-2 px-3 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center justify-center space-x-2 transition shadow-sm"
              @click="emit('open-qr-scanner')"
            >
              <QrCode class="w-4 h-4" />
              <span>Fazer Check-in</span>
            </button>
            <button
              class="py-2 px-3 rounded-md bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 text-xs font-semibold flex items-center justify-center space-x-1.5 transition"
              @click="promptCancel(b)"
            >
              <XCircle class="w-3.5 h-3.5" />
              <span>Cancelar</span>
            </button>
          </div>

          <!-- Checked In: Early checkout / Release button -->
          <div v-else-if="b.status === 'CHECKED_IN'" class="pt-1">
            <button
              class="w-full py-2 px-3 rounded-md bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-semibold flex items-center justify-center space-x-2 transition"
              @click="promptCheckout(b)"
            >
              <LogOut class="w-4 h-4" />
              <span>Liberar Baia / Saída Antecipada</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog Modal -->
    <div
      v-if="confirmModalOpen && targetBooking"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
        <div class="flex items-start space-x-3">
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
            :class="confirmActionType === 'checkout' ? 'bg-amber-500/10 text-amber-400' : 'bg-red-500/10 text-red-400'"
          >
            <AlertTriangle class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-base font-bold text-ink">
              {{ confirmActionType === 'checkout' ? 'Liberar Baia Antecipadamente?' : 'Cancelar Reserva de Baia?' }}
            </h3>
            <p class="text-xs text-ink-subtle mt-1 leading-relaxed">
              <span v-if="confirmActionType === 'checkout'">
                Você confirmou presença na <strong>Baia #{{ targetBooking.desk_id }}</strong>. Ao liberar a baia mais cedo,
                o espaço é desocupado imediatamente e o horário restante fica livre para outros colaboradores utilizarem.
              </span>
              <span v-else>
                Deseja realmente cancelar a reserva da <strong>Baia #{{ targetBooking.desk_id }}</strong>? A baia voltará a ficar disponível para outros colaboradores agendarem.
              </span>
            </p>
          </div>
        </div>

        <div class="flex items-center justify-end space-x-2 pt-2 border-t border-hairline">
          <button
            class="px-3 py-1.5 text-xs text-ink-subtle hover:text-ink transition"
            :disabled="isProcessingAction"
            @click="confirmModalOpen = false"
          >
            Voltar
          </button>
          <button
            class="px-4 py-1.5 text-xs font-semibold rounded-md text-white transition flex items-center space-x-1.5 shadow-sm"
            :class="confirmActionType === 'checkout' ? 'bg-amber-600 hover:bg-amber-500' : 'bg-red-600 hover:bg-red-500'"
            :disabled="isProcessingAction"
            @click="executeAction"
          >
            <RefreshCw v-if="isProcessingAction" class="w-3.5 h-3.5 animate-spin" />
            <span>{{ confirmActionType === 'checkout' ? 'Sim, Liberar Agora' : 'Sim, Cancelar' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
