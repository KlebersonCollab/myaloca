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
  Users,
  Headphones,
  Lock,
  ShieldAlert,
  LogOut,
  RefreshCw,
} from 'lucide-vue-next';
import { api } from '../services/api';
import { useAuth } from '../stores/auth';
import type { DeskWithOccupant } from '../types';

const props = defineProps<{
  desk: DeskWithOccupant | null;
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'booking-created'): void;
}>();

const { currentUser } = useAuth();

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

const isRoleForbidden = computed(() => {
  if (!props.desk?.required_role) return false;
  const userRole = currentUser.value?.role;
  if (props.desk.required_role === 'gestor') {
    return userRole !== 'gestor' && userRole !== 'admin';
  }
  if (props.desk.required_role === 'admin') {
    return userRole !== 'admin';
  }
  return false;
});

const durationMinutes = computed(() => {
  if (!startTime.value || !endTime.value) return 0;
  const [sh, sm] = startTime.value.split(':').map(Number);
  const [eh, em] = endTime.value.split(':').map(Number);
  return eh * 60 + em - (sh * 60 + sm);
});

const isDurationExceeded = computed(() => {
  if (!props.desk?.max_duration_minutes) return false;
  return durationMinutes.value > props.desk.max_duration_minutes;
});

async function handleBook() {
  if (!props.desk) return;
  if (isRoleForbidden.value) {
    errorMessage.value = 'Acesso restrito: este espaço é exclusivo para gestores.';
    return;
  }
  if (isDurationExceeded.value) {
    errorMessage.value = `A duração excede o limite máximo permitido de ${props.desk.max_duration_minutes} minutos para este espaço.`;
    return;
  }

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
      errorMessage.value = 'Conflito: Este espaço já possui reserva para este intervalo de horário.';
    } else if (err.code === 'MAX_DURATION_EXCEEDED') {
      errorMessage.value = 'Duração máxima excedida para este espaço.';
    } else if (err.code === 'RESERVATION_RESTRICTED_ROLE') {
      errorMessage.value = 'Acesso negado: este espaço é exclusivo para gestores.';
    } else {
      errorMessage.value = err.message || 'Erro ao criar reserva.';
    }
  } finally {
    isSubmitting.value = false;
  }
}

const isCurrentUserOccupant = computed(() => {
  return (
    props.desk?.occupant_name &&
    currentUser.value?.full_name === props.desk.occupant_name
  );
});

const canReleaseDesk = computed(() => {
  const role = currentUser.value?.role;
  return role === 'admin' || role === 'gestor' || isCurrentUserOccupant.value;
});

const isReleasingDesk = ref(false);

async function handleReleaseFromModal() {
  if (!props.desk) return;
  isReleasingDesk.value = true;
  errorMessage.value = null;
  successMessage.value = null;

  try {
    await api.desks.release(props.desk.id);
    successMessage.value = `Baia ${props.desk.code} liberada com sucesso! O assento já está disponível.`;
    setTimeout(() => {
      emit('booking-created');
      emit('close');
    }, 1200);
  } catch (err: any) {
    errorMessage.value = err.message || 'Falha ao liberar baia.';
  } finally {
    isReleasingDesk.value = false;
  }
}

watch(
  () => props.isOpen,
  (val) => {
    if (val && props.desk) {
      errorMessage.value = null;
      successMessage.value = null;
      notes.value = '';

      // Default duration intelligently according to room policy
      if (props.desk.max_duration_minutes && props.desk.max_duration_minutes < 540) {
        const maxM = props.desk.max_duration_minutes;
        const [h, m] = startTime.value.split(':').map(Number);
        const totalM = h * 60 + m + maxM;
        const eh = Math.min(23, Math.floor(totalM / 60));
        const em = totalM % 60;
        endTime.value = `${String(eh).padStart(2, '0')}:${String(em).padStart(2, '0')}`;
      } else {
        endTime.value = '18:00';
      }
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
            <!-- Status Badge -->
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

          <!-- Space Type Subtitle -->
          <div class="flex items-center space-x-2 mt-1">
            <span
              v-if="desk.space_type === 'SALA_REUNIAO'"
              class="inline-flex items-center space-x-1 px-1.5 py-0.5 text-[10px] font-bold rounded bg-purple-500/15 text-purple-400 border border-purple-500/30"
            >
              <Users class="w-3 h-3" />
              <span>Sala de Reunião ({{ desk.capacity || 4 }} pessoas)</span>
            </span>
            <span
              v-else-if="desk.space_type === 'CABINE_FOCUS'"
              class="inline-flex items-center space-x-1 px-1.5 py-0.5 text-[10px] font-bold rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30"
            >
              <Headphones class="w-3 h-3" />
              <span>Cabine Focus (Individual)</span>
            </span>
            <span
              v-else
              class="inline-flex items-center space-x-1 px-1.5 py-0.5 text-[10px] font-medium rounded bg-surface-2 text-ink-subtle border border-hairline"
            >
              <span>Baia de Trabalho</span>
            </span>

            <span class="text-xs text-ink-subtle">
              • Posição: ({{ desk.pos_x }}m, {{ desk.pos_z }}m)
            </span>
          </div>
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
        <!-- Policies / Limits Banner -->
        <div
          v-if="desk.max_duration_minutes || desk.required_role"
          class="p-2.5 rounded-lg bg-surface-2 border border-hairline space-y-1.5 text-xs"
        >
          <div v-if="desk.max_duration_minutes" class="flex items-center space-x-1.5 text-amber-400 font-medium">
            <Clock class="w-3.5 h-3.5 shrink-0" />
            <span>
              Tempo Máximo: <strong>{{ desk.max_duration_minutes >= 60 ? `${desk.max_duration_minutes / 60}h` : `${desk.max_duration_minutes} min` }}</strong> por reserva
            </span>
          </div>
          <div
            v-if="desk.required_role"
            class="flex items-center space-x-1.5"
            :class="isRoleForbidden ? 'text-red-400 font-semibold' : 'text-purple-400'"
          >
            <Lock class="w-3.5 h-3.5 shrink-0" />
            <span>
              Restrição de Perfil: <strong>Exclusivo para Gestores</strong>
            </span>
          </div>
        </div>

        <!-- Role Forbidden Warning Alert -->
        <div
          v-if="isRoleForbidden"
          class="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400 flex items-start space-x-2"
        >
          <ShieldAlert class="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
          <div>
            <strong>Espaço Restrito:</strong> Seu perfil atual ({{ currentUser?.role }}) não possui permissão para reservar este espaço. Solicite a um gestor ou selecione uma baia de uso livre.
          </div>
        </div>

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

          <!-- Duration Exceeded Warning -->
          <div
            v-if="isDurationExceeded"
            class="p-2 bg-red-500/10 border border-red-500/20 rounded-md text-xs text-red-400 flex items-center space-x-1.5"
          >
            <AlertTriangle class="w-4 h-4 shrink-0 text-red-400" />
            <span>
              Duração selecionada (<strong>{{ durationMinutes }} min</strong>) excede o limite máximo permitido de <strong>{{ desk.max_duration_minutes }} min</strong>.
            </span>
          </div>

          <!-- Auto-Release Rule Warning Alert -->
          <div class="bg-amber-500/10 border border-amber-500/20 p-2.5 rounded-md text-xs text-amber-300 flex items-start space-x-2">
            <AlertTriangle class="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
            <div>
              <strong>Tolerância de Check-in:</strong> Você deve fazer check-in físico escaneando o QR Code no local até às <strong>{{ checkinDeadlinePreview }}</strong>, senão a reserva será cancelada e liberada automaticamente.
            </div>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Observações (opcional)</label>
            <input
              v-model="notes"
              type="text"
              placeholder="Ex: Reunião de Alinhamento com Time"
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
              :disabled="isSubmitting || isRoleForbidden || isDurationExceeded"
              class="w-full bg-primary hover:bg-primary-hover disabled:opacity-50 text-white font-medium py-2.5 px-4 rounded-md text-sm transition shadow-sm shadow-primary/25 active:scale-98"
            >
              <span v-if="isRoleForbidden">Acesso Restrito a Gestores</span>
              <span v-else-if="isDurationExceeded">Duração Acima do Permitido</span>
              <span v-else-if="isSubmitting">Processando reserva...</span>
              <span v-else-if="desk.space_type === 'SALA_REUNIAO'">Confirmar Reserva da Sala</span>
              <span v-else-if="desk.space_type === 'CABINE_FOCUS'">Confirmar Reserva da Cabine</span>
              <span v-else>Confirmar Reserva de Baia</span>
            </button>
          </div>
        </form>

        <!-- If Not Available: Show Release Option for Admin / Gestor / Occupant -->
        <div v-else class="space-y-4">
          <div
            v-if="canReleaseDesk"
            class="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl space-y-3"
          >
            <div class="flex items-center space-x-2 text-amber-400 font-bold text-xs">
              <LogOut class="w-4 h-4" />
              <span>Liberação de Baia {{ currentUser?.role === 'admin' || currentUser?.role === 'gestor' ? '(Ação de Gestor)' : '' }}</span>
            </div>
            <p class="text-xs text-ink-subtle leading-relaxed">
              O integrante já saiu ou desocupou o espaço? Como {{ currentUser?.role === 'admin' ? 'administrador' : (currentUser?.role === 'gestor' ? 'gestor' : 'titular') }}, você pode liberar a baia imediatamente para que outros colaboradores possam reservá-la.
            </p>

            <div v-if="errorMessage" class="p-2 bg-red-500/10 border border-red-500/20 rounded-md text-xs text-red-400">
              {{ errorMessage }}
            </div>
            <div v-if="successMessage" class="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-md text-xs text-emerald-400 flex items-center space-x-2">
              <CheckCircle2 class="w-4 h-4" />
              <span>{{ successMessage }}</span>
            </div>

            <button
              type="button"
              :disabled="isReleasingDesk"
              class="w-full py-2.5 px-4 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition shadow-sm flex items-center justify-center space-x-2 disabled:opacity-50"
              @click="handleReleaseFromModal"
            >
              <RefreshCw v-if="isReleasingDesk" class="w-3.5 h-3.5 animate-spin" />
              <LogOut v-else class="w-3.5 h-3.5" />
              <span>{{ isReleasingDesk ? 'Liberando...' : 'Liberar Baia / Cancelar Reserva Agora' }}</span>
            </button>
          </div>

          <div v-else class="text-xs text-ink-subtle text-center py-4 bg-surface-2 rounded-lg">
            Este espaço está atualmente {{ desk.status === 'OCUPADA' ? 'ocupado' : 'reservado' }} e indisponível para novos agendamentos.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
