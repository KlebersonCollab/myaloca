<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Shield, Plus, Download, RefreshCw, X } from 'lucide-vue-next';
import { api } from '../services/api';
import type { Desk, Zone } from '../types';

const desks = ref<Desk[]>([]);
const zones = ref<Zone[]>([]);
const isLoading = ref(false);
const showCreateModal = ref(false);

// New Desk Form
const newDesk = ref({
  code: '',
  zone_id: 1,
  pos_x: 0.0,
  pos_y: 0.0,
  pos_z: 0.0,
  rotation_y: 0.0,
  has_monitor: true,
  has_docking_station: true,
  is_standing_desk: false,
});
const isCreating = ref(false);
const createError = ref<string | null>(null);

async function loadData() {
  isLoading.value = true;
  try {
    const [fetchedZones, fetchedDesks] = await Promise.all([
      api.zones.list(),
      api.desks.list(),
    ]);
    zones.value = fetchedZones;
    desks.value = fetchedDesks;
    if (zones.value.length > 0) {
      newDesk.value.zone_id = zones.value[0].id;
    }
  } catch {
    // ignore
  } finally {
    isLoading.value = false;
  }
}

async function handleCreateDesk() {
  isCreating.value = true;
  createError.value = null;
  try {
    await api.desks.create(newDesk.value);
    showCreateModal.value = false;
    newDesk.value.code = '';
    await loadData();
  } catch (err: any) {
    createError.value = err.message || 'Falha ao cadastrar baia.';
  } finally {
    isCreating.value = false;
  }
}

function getQrDownloadUrl(deskId: number) {
  return api.desks.getQrCodeUrl(deskId);
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-ink tracking-tight flex items-center space-x-2">
          <Shield class="w-5 h-5 text-purple-400" />
          <span>Painel do Gestor: Gestão de Baias & QR Codes</span>
        </h2>
        <p class="text-xs text-ink-subtle mt-1">
          Cadastre novas estações com coordenadas 3D e exporte QR-Codes imutáveis para impressão física.
        </p>
      </div>

      <div class="flex items-center space-x-3">
        <button
          class="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
          @click="loadData"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
          <span>Atualizar</span>
        </button>
        <button
          class="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
          @click="showCreateModal = true"
        >
          <Plus class="w-4 h-4" />
          <span>Cadastrar Baia 3D</span>
        </button>
      </div>
    </div>

    <!-- Desks Table -->
    <div class="bg-surface-1 border border-hairline rounded-xl overflow-hidden shadow-xl">
      <table class="w-full text-left text-xs">
        <thead class="bg-surface-2/60 border-b border-hairline text-ink-muted uppercase font-semibold">
          <tr>
            <th class="px-4 py-3">Código</th>
            <th class="px-4 py-3">Zona / Andar</th>
            <th class="px-4 py-3">Coordenadas 3D (X, Y, Z)</th>
            <th class="px-4 py-3">Equipamentos</th>
            <th class="px-4 py-3">Status</th>
            <th class="px-4 py-3 text-right">QR Code Físico</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-hairline text-ink">
          <tr v-for="d in desks" :key="d.id" class="hover:bg-surface-2/30 transition">
            <td class="px-4 py-3.5 font-bold text-ink">
              {{ d.code }}
            </td>
            <td class="px-4 py-3.5 text-ink-muted">
              Zona #{{ d.zone_id }}
            </td>
            <td class="px-4 py-3.5 font-mono text-ink-subtle">
              ({{ d.pos_x.toFixed(1) }}, {{ d.pos_y.toFixed(1) }}, {{ d.pos_z.toFixed(1) }})
            </td>
            <td class="px-4 py-3.5">
              <div class="flex items-center space-x-2 text-ink-subtle">
                <span v-if="d.has_monitor" class="text-primary font-medium">Monitor</span>
                <span v-if="d.has_docking_station">• Dock</span>
                <span v-if="d.is_standing_desk">• Standing</span>
              </div>
            </td>
            <td class="px-4 py-3.5">
              <span
                class="px-2 py-0.5 text-[10px] font-semibold rounded uppercase"
                :class="{
                  'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20':
                    d.status === 'DISPONIVEL',
                  'bg-amber-500/10 text-amber-400 border border-amber-500/20':
                    d.status === 'RESERVADA',
                  'bg-primary/10 text-primary border border-primary/20': d.status === 'OCUPADA',
                  'bg-hairline text-ink-subtle': d.status === 'MANUTENCAO',
                }"
              >
                {{ d.status }}
              </span>
            </td>
            <td class="px-4 py-3.5 text-right">
              <a
                :href="getQrDownloadUrl(d.id)"
                target="_blank"
                class="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
                title="Abrir e imprimir QR Code físico"
              >
                <Download class="w-3.5 h-3.5 text-primary" />
                <span>Exportar PNG</span>
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Desk Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-xl w-full max-w-md shadow-2xl p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <h3 class="font-bold text-ink text-sm">Cadastrar Nova Baia 3D</h3>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="showCreateModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-3" @submit.prevent="handleCreateDesk">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Código Identificador</label>
            <input
              v-model="newDesk.code"
              type="text"
              required
              placeholder="Ex: BAIA-B105"
              class="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Zona / Andar</label>
            <select
              v-model="newDesk.zone_id"
              class="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            >
              <option v-for="z in zones" :key="z.id" :value="z.id">
                {{ z.name }}
              </option>
            </select>
          </div>

          <!-- 3D Coordinates -->
          <div class="grid grid-cols-3 gap-2">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Pos X (m)</label>
              <input
                v-model.number="newDesk.pos_x"
                type="number"
                step="0.5"
                required
                class="w-full bg-surface-2 border border-hairline rounded-md px-2 py-1.5 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Pos Y (m)</label>
              <input
                v-model.number="newDesk.pos_y"
                type="number"
                step="0.5"
                required
                class="w-full bg-surface-2 border border-hairline rounded-md px-2 py-1.5 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Pos Z (m)</label>
              <input
                v-model.number="newDesk.pos_z"
                type="number"
                step="0.5"
                required
                class="w-full bg-surface-2 border border-hairline rounded-md px-2 py-1.5 text-xs text-ink focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <!-- Equipments checkboxes -->
          <div class="space-y-2 pt-2 text-xs text-ink-muted">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="newDesk.has_monitor" type="checkbox" class="accent-primary" />
              <span>Possui Monitor Duplo</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="newDesk.has_docking_station" type="checkbox" class="accent-primary" />
              <span>Possui Docking Station</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="newDesk.is_standing_desk" type="checkbox" class="accent-primary" />
              <span>Mesa Ajustável (Standing Desk)</span>
            </label>
          </div>

          <div v-if="createError" class="p-2 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded">
            {{ createError }}
          </div>

          <button
            type="submit"
            :disabled="isCreating"
            class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-md transition"
          >
            {{ isCreating ? 'Salvando...' : 'Cadastrar e Gerar QR Code Imutável' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
