<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  Calendar,
  Clock,
  Monitor,
  CheckCircle2,
  AlertTriangle,
  X,
  User as UserIcon,
} from 'lucide-vue-next';
import { api } from '../services/api';
import type { DeskWithOccupant } from '../types';

const props = defineProps<{
  desk: DeskWithOccupant | null;
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'booking-created'): void;
}>();

const date = ref(new Date().toISOString().split('T')[0]);
const startTime = ref('09:00');
const endTime = ref('18:00');
const notes = ref('');
const isSubmitting = ref(false);
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);

const checkinDeadlinePreview = computed(() => {
  if (!startTime.value) return '';
  const [h, m] = startTime.value.split(':').map(Number);
  const totalMin = h * 60 + m + 30;
  const dh = Math.floor(totalMin / 60) % 24;
  const dm = totalMin % 60;
  return `${String(dh).padStart(2, '0')}:${String(dm).padStart(2, '0')}`;
});

async function handleBook() {
  if (!props.desk) return;
  isSubmitting.value = true;
  errorMessage.value = null;
  successMessage.value = null;

  try {
    const startIso = new Date(`${date.value}T${startTime.value}:00`).toISOString();
    const endIso = new Date(`${date.value}T${endTime.value}:00`).toISOString();

    if (new Date(startIso) >= new Date(endIso)) {
      throw new Error('O horário de início deve ser anterior ao término.');
    }

    await api.bookings.create({
      desk_id: props.desk.id,
      start_time: startIso,
      end_time: endIso,
      notes: notes.value || undefined,
    });

    successMessage.value = 'Reserva confirmada com sucesso!';
    setTimeout(() => {
      emit('booking-created');
      emit('close');
    }, 1200);
  } catch (err: any) {
    if (err.code === 'BOOKING_OVERLAP') {
      errorMessage.value = 'Conflito: Esta baia já possui reserva para este intervalo de horário.';
    } else {
      errorMessage.value = err.message || 'Erro ao criar reserva.';
    }
  } finally {
    isSubmitting.value = false;
  }
}

watch(
  () => props.isOpen,
  (val) => {
    if (val) {
      errorMessage.value = null;
      successMessage.value = null;
      notes.value = '';
    }
  }
);
</script>

<template>
  <div
    v-if="isOpen && desk"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4"
  >
    <div
      class="bg-surface-1 border border-hairline-strong rounded-xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Header -->
      <div class="px-5 py-4 border-b border-hairline flex items-center justify-between bg-surface-2/50">
        <div>
          <div class="flex items-center space-x-2">
            <h3 class="font-bold text-ink text-base">{{ desk.code }}</h3>
            <span
              class="px-2 py-0.5 text-[10px] font-semibold rounded uppercase"
              :class="{
                'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20':
                  desk.status === 'DISPONIVEL',
                'bg-amber-500/10 text-amber-400 border border-amber-500/20':
                  desk.status === 'RESERVADA',
                'bg-primary/10 text-primary border border-primary/20': desk.status === 'OCUPADA',
                'bg-hairline text-ink-subtle': desk.status === 'MANUTENCAO',
              }"
            >
              {{ desk.status }}
            </span>
          </div>
          <p class="text-xs text-ink-subtle">
            Posição 3D: ({{ desk.pos_x }}m, {{ desk.pos_z }}m)
          </p>
        </div>
        <button
          class="p-1 rounded-md text-ink-subtle hover:text-ink hover:bg-surface-3 transition"
          @click="emit('close')"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Content -->
      <div class="p-5 space-y-4">
        <!-- Desk Features -->
        <div class="flex items-center space-x-4 text-xs text-ink-muted bg-surface-2 p-2.5 rounded-lg border border-hairline">
          <div class="flex items-center space-x-1.5" :class="desk.has_monitor ? 'text-primary' : 'text-ink-tertiary'">
            <Monitor class="w-4 h-4" />
            <span>{{ desk.has_monitor ? 'Monitor Duplo' : 'Sem Monitor' }}</span>
          </div>
          <div v-if="desk.has_docking_station" class="text-emerald-400">
            • Docking Station
          </div>
          <div v-if="desk.is_standing_desk" class="text-purple-400">
            • Standing Desk
          </div>
        </div>

        <!-- If Occupied / Reserved by someone -->
        <div
          v-if="desk.occupant_name"
          class="p-3 bg-surface-2/80 rounded-lg border border-hairline flex items-center space-x-3"
        >
          <div class="w-10 h-10 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center overflow-hidden">
            <img
              v-if="desk.occupant_avatar || desk.occupant_photo"
              :src="desk.occupant_avatar || desk.occupant_photo || ''"
              class="w-full h-full object-cover"
            />
            <UserIcon v-else class="w-5 h-5 text-primary" />
          </div>
          <div>
            <div class="text-xs text-ink-subtle">Ocupante atual:</div>
            <div class="text-sm font-semibold text-ink">{{ desk.occupant_name }}</div>
          </div>
        </div>

        <!-- Booking Form (If Available) -->
        <form v-if="desk.status === 'DISPONIVEL'" class="space-y-3" @submit.prevent="handleBook">
          <!-- Date -->
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1 flex items-center space-x-1.5">
              <Calendar class="w-3.5 h-3.5" />
              <span>Data da Reserva</span>
            </label>
            <input
              v-model="date"
              type="date"
              required
              class="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <!-- Time Range -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1 flex items-center space-x-1.5">
                <Clock class="w-3.5 h-3.5" />
                <span>Horário Início</span>
              </label>
              <input
                v-model="startTime"
                type="time"
                required
                class="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1 flex items-center space-x-1.5">
                <Clock class="w-3.5 h-3.5" />
                <span>Horário Término</span>
              </label>
              <input
                v-model="endTime"
                type="time"
                required
                class="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <!-- Auto-Release Rule Warning Alert -->
          <div class="bg-amber-500/10 border border-amber-500/20 p-2.5 rounded-md text-xs text-amber-300 flex items-start space-x-2">
            <AlertTriangle class="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
            <div>
              <strong>Tolerância de Check-in:</strong> Você deve fazer check-in físico escaneando o QR Code na mesa até às <strong>{{ checkinDeadlinePreview }}</strong>, senão a baia será liberada para outros colegas.
            </div>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Observações (opcional)</label>
            <input
              v-model="notes"
              type="text"
              placeholder="Ex: Trabalho com equipe de Design"
              class="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-tertiary focus:outline-none focus:border-primary"
            />
          </div>

          <!-- Error / Success messages -->
          <div v-if="errorMessage" class="p-2.5 bg-red-500/10 border border-red-500/20 rounded-md text-xs text-red-400">
            {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-md text-xs text-emerald-400 flex items-center space-x-2">
            <CheckCircle2 class="w-4 h-4" />
            <span>{{ successMessage }}</span>
          </div>

          <!-- Submit Button -->
          <div class="pt-2">
            <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full bg-primary hover:bg-primary-hover disabled:opacity-50 text-white font-medium py-2.5 px-4 rounded-md text-sm transition shadow-sm shadow-primary/25 active:scale-98"
            >
              {{ isSubmitting ? 'Processando reserva...' : 'Confirmar Reserva de Baia' }}
            </button>
          </div>
        </form>

        <div v-else class="text-xs text-ink-subtle text-center py-3 bg-surface-2 rounded-lg">
          Esta baia não está disponível para nova reserva no momento.
        </div>
      </div>
    </div>
  </div>
</template>
