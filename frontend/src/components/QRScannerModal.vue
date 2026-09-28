<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue';
import { Html5Qrcode } from 'html5-qrcode';
import { QrCode, X, CheckCircle2, Camera, KeyRound } from 'lucide-vue-next';
import { api } from '../services/api';
import type { Booking } from '../types';

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'checkin-success', booking: Booking): void;
}>();

const activeTab = ref<'camera' | 'manual'>('camera');
const manualCode = ref('');
const isProcessing = ref(false);
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);
let qrScanner: Html5Qrcode | null = null;

async function startCamera() {
  errorMessage.value = null;
  try {
    qrScanner = new Html5Qrcode('qr-reader-container');
    await qrScanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 220, height: 220 } },
      (decodedText) => {
        handleQrDecoded(decodedText);
      },
      () => {
        // frame decode ignore
      }
    );
  } catch (err: any) {
    errorMessage.value = 'Não foi possível acessar a câmera. Use a entrada manual abaixo.';
    activeTab.value = 'manual';
  }
}

async function stopCamera() {
  if (qrScanner) {
    try {
      await qrScanner.stop();
      qrScanner.clear();
    } catch {
      // ignore stop errors
    }
    qrScanner = null;
  }
}

async function handleQrDecoded(text: string) {
  // Extract hash from URL or use raw text
  let extractedHash = text;
  if (text.includes('hash=')) {
    const url = new URL(text);
    extractedHash = url.searchParams.get('hash') || text;
  }

  await processCheckIn(extractedHash);
}

async function processCheckIn(hash: string) {
  isProcessing.value = true;
  errorMessage.value = null;
  successMessage.value = null;

  try {
    // 1. Fetch user's pending bookings
    const myBookings = await api.bookings.listMy();
    const pendingBooking = myBookings.find((b) => b.status === 'PENDENTE_CHECKIN');

    if (!pendingBooking) {
      throw new Error('Você não possui reservas pendentes de check-in para hoje.');
    }

    // 2. Perform check-in
    const updated = await api.bookings.checkIn(pendingBooking.id, hash);
    successMessage.value = 'Presença confirmada fisicamente com sucesso na baia!';
    await stopCamera();

    setTimeout(() => {
      emit('checkin-success', updated);
      emit('close');
    }, 1200);
  } catch (err: any) {
    errorMessage.value = err.message || 'Falha ao validar QR Code de check-in.';
  } finally {
    isProcessing.value = false;
  }
}

async function handleManualSubmit() {
  if (!manualCode.value.trim()) return;
  await processCheckIn(manualCode.value.trim());
}

watch(
  () => props.isOpen,
  async (open) => {
    if (open) {
      errorMessage.value = null;
      successMessage.value = null;
      manualCode.value = '';
      if (activeTab.value === 'camera') {
        setTimeout(startCamera, 200);
      }
    } else {
      await stopCamera();
    }
  }
);

watch(activeTab, async (tab) => {
  if (tab === 'camera' && props.isOpen) {
    setTimeout(startCamera, 150);
  } else {
    await stopCamera();
  }
});

onBeforeUnmount(async () => {
  await stopCamera();
});
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
  >
    <div
      class="bg-surface-1 border border-hairline-strong rounded-xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Header -->
      <div class="px-5 py-4 border-b border-hairline flex items-center justify-between bg-surface-2/50">
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
            <QrCode class="w-4 h-4" />
          </div>
          <div>
            <h3 class="font-bold text-ink text-sm">Check-in Presencial</h3>
            <p class="text-[11px] text-ink-subtle">Validação física por QR Code</p>
          </div>
        </div>
        <button
          class="p-1 rounded-md text-ink-subtle hover:text-ink hover:bg-surface-3 transition"
          @click="emit('close')"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Mode Switcher -->
      <div class="flex border-b border-hairline bg-surface-2 text-xs">
        <button
          class="flex-1 py-2.5 flex items-center justify-center space-x-1.5 transition font-medium"
          :class="
            activeTab === 'camera'
              ? 'text-primary border-b-2 border-primary bg-surface-1'
              : 'text-ink-subtle hover:text-ink'
          "
          @click="activeTab = 'camera'"
        >
          <Camera class="w-3.5 h-3.5" />
          <span>Escanear com Câmera</span>
        </button>
        <button
          class="flex-1 py-2.5 flex items-center justify-center space-x-1.5 transition font-medium"
          :class="
            activeTab === 'manual'
              ? 'text-primary border-b-2 border-primary bg-surface-1'
              : 'text-ink-subtle hover:text-ink'
          "
          @click="activeTab = 'manual'"
        >
          <KeyRound class="w-3.5 h-3.5" />
          <span>Código Manual / Hash</span>
        </button>
      </div>

      <!-- Body -->
      <div class="p-5 space-y-4">
        <!-- Camera Scanner Element -->
        <div v-show="activeTab === 'camera'" class="space-y-3">
          <div
            id="qr-reader-container"
            class="w-full aspect-square bg-black/40 rounded-lg overflow-hidden border border-hairline flex items-center justify-center"
          />
          <p class="text-center text-[11px] text-ink-subtle">
            Aponte a câmera para o QR Code impresso e fixado na baia de trabalho.
          </p>
        </div>

        <!-- Manual Input Tab -->
        <div v-show="activeTab === 'manual'" class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">
              Token Criptográfico da Baia
            </label>
            <input
              v-model="manualCode"
              type="text"
              placeholder="Cole o hash ou leia o código da mesa..."
              class="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-tertiary focus:outline-none focus:border-primary"
            />
          </div>
          <button
            :disabled="isProcessing || !manualCode"
            class="w-full bg-primary hover:bg-primary-hover disabled:opacity-50 text-white font-medium py-2 rounded-md text-sm transition"
            @click="handleManualSubmit"
          >
            {{ isProcessing ? 'Validando...' : 'Confirmar Presença' }}
          </button>
        </div>

        <!-- Messages -->
        <div v-if="errorMessage" class="p-2.5 bg-red-500/10 border border-red-500/20 rounded-md text-xs text-red-400">
          {{ errorMessage }}
        </div>
        <div
          v-if="successMessage"
          class="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-md text-xs text-emerald-400 flex items-center space-x-2"
        >
          <CheckCircle2 class="w-4 h-4" />
          <span>{{ successMessage }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
