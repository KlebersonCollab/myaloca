<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  Shield,
  Plus,
  Download,
  RefreshCw,
  X,
  QrCode,
  Printer,
  Check,
  Copy,
  Building2,
  Sparkles,
  MousePointerClick,
  Monitor,
  Users,
  Headphones,
  Lock,
  Clock,
  Trash2,
  AlertTriangle,
  Layers,
  Edit3,
  MapPin,
  Briefcase,
  LogOut,
} from 'lucide-vue-next';
import { api } from '../services/api';
import type { Building, Company, Desk, SpaceType, UserRole, Zone } from '../types';

// Tab selection
const activeTab = ref<'buildings' | 'floors' | 'desks'>('desks');

// Data State
const companies = ref<Company[]>([]);
const buildings = ref<Building[]>([]);
const zones = ref<Zone[]>([]);
const desks = ref<Desk[]>([]);
const isLoading = ref(false);

// Filters
const selectedBuildingFilter = ref<number | null>(null);
const selectedFloor = ref<number | null>(1);

// Modals visibility
const showBuildingModal = ref(false);
const editingBuilding = ref<Building | null>(null);
const buildingToDelete = ref<Building | null>(null);
const isDeletingBuilding = ref(false);
const deleteBuildingError = ref<string | null>(null);

const showCompanyModal = ref(false);
const isCreatingCompany = ref(false);
const companyError = ref<string | null>(null);

const showNewZoneModal = ref(false);
const editingZone = ref<Zone | null>(null);
const zoneToDelete = ref<Zone | null>(null);
const isDeletingZone = ref(false);
const deleteZoneError = ref<string | null>(null);

const showCreateModal = ref(false); // Bench Assistant
const showRoomModal = ref(false); // Special Room Modal
const editingDesk = ref<Desk | null>(null);
const isUpdatingDesk = ref(false);
const editDeskError = ref<string | null>(null);

const selectedDeskForQr = ref<Desk | null>(null);
const deskToDelete = ref<Desk | null>(null);
const isDeleting = ref(false);
const deleteError = ref<string | null>(null);
const isDownloadingQr = ref(false);
const copiedHash = ref(false);

// Forms
const companyForm = ref({
  name: '',
  code: '',
  cnpj: '',
  description: '',
});

const buildingForm = ref({
  name: '',
  code: '',
  company_id: 1 as number | null,
  address: '',
  city: '',
  total_floors: 10,
});
const buildingError = ref<string | null>(null);
const isSavingBuilding = ref(false);

const newZoneForm = ref({
  building_id: null as number | null,
  floor: 2,
  name: '',
  description: '',
});
const isCreatingZone = ref(false);
const zoneError = ref<string | null>(null);

const benchForm = ref({
  zone_id: 1,
  prefix: 'B',
  count: 4,
  layout: 'face-to-face' as 'face-to-face' | 'single-row',
  has_monitor: true,
  has_docking_station: true,
  is_standing_desk: false,
});
const isCreatingBatch = ref(false);
const batchError = ref<string | null>(null);

const roomForm = ref({
  zone_id: 1,
  code: '',
  space_type: 'SALA_REUNIAO' as SpaceType,
  capacity: 6,
  required_role: '' as '' | UserRole,
  max_duration_minutes: 60 as number | null,
  has_monitor: true,
  has_docking_station: true,
  is_standing_desk: false,
});
const isCreatingRoom = ref(false);
const roomError = ref<string | null>(null);

const editDeskForm = ref({
  code: '',
  zone_id: 1,
  space_type: 'BAIA' as SpaceType,
  capacity: 1,
  required_role: '' as '' | UserRole,
  max_duration_minutes: null as number | null,
  has_monitor: false,
  has_docking_station: false,
  is_standing_desk: false,
});

// Grid click-to-place state
const isClickPlacing = ref(false);

// ==========================================
// Computed Properties
// ==========================================
const availableFloors = computed(() => {
  const floors = new Set<number>();
  zones.value.forEach((z) => {
    if (selectedBuildingFilter.value !== null && z.building_id !== selectedBuildingFilter.value) {
      return;
    }
    if (z.floor !== undefined && z.floor !== null) {
      floors.add(z.floor);
    }
  });
  return Array.from(floors).sort((a, b) => a - b);
});

const filteredZones = computed(() => {
  return zones.value.filter((z) => {
    if (selectedBuildingFilter.value !== null && z.building_id !== selectedBuildingFilter.value) {
      return false;
    }
    if (selectedFloor.value !== null && z.floor !== selectedFloor.value) {
      return false;
    }
    return true;
  });
});

const filteredDesks = computed(() => {
  const zoneIds = new Set(filteredZones.value.map((z) => z.id));
  return desks.value.filter((d) => zoneIds.has(d.zone_id));
});

const previewDesks = computed(() => {
  const list = [];
  const count = Math.max(1, Math.min(benchForm.value.count, 12));
  const isFaceToFace = benchForm.value.layout === 'face-to-face';

  for (let i = 1; i <= count; i++) {
    const code = `${benchForm.value.prefix.toUpperCase()}-${String(i).padStart(2, '0')}`;
    let posX = 0;
    let posZ = 0;
    let rotY = 0;

    if (isFaceToFace) {
      const half = Math.ceil(count / 2);
      if (i <= half) {
        posX = (i - (half + 1) / 2) * 2.4;
        posZ = -1.2;
        rotY = 0;
      } else {
        const col = i - half;
        posX = (col - (half + 1) / 2) * 2.4;
        posZ = 1.2;
        rotY = 180;
      }
    } else {
      posX = (i - (count + 1) / 2) * 2.4;
      posZ = 0;
      rotY = 0;
    }

    list.push({
      code,
      pos_x: Number(posX.toFixed(2)),
      pos_y: 0.0,
      pos_z: Number(posZ.toFixed(2)),
      rotation_y: rotY,
    });
  }
  return list;
});

// Interactive 2D Grid
const gridRows = 4;
const gridCols = 6;

function getDeskAtGridCell(row: number, col: number): Desk | undefined {
  const targetX = Number(((col - (gridCols - 1) / 2) * 2.4).toFixed(2));
  const targetZ = Number(((row - (gridRows - 1) / 2) * 2.4).toFixed(2));

  return filteredDesks.value.find((d) => {
    return Math.abs(d.pos_x - targetX) < 1.0 && Math.abs(d.pos_z - targetZ) < 1.0;
  });
}

// ==========================================
// Data Loader
// ==========================================
async function loadData() {
  isLoading.value = true;
  try {
    const [fetchedCompanies, fetchedBuildings, fetchedZones, fetchedDesks] = await Promise.all([
      api.companies.list(),
      api.buildings.list(),
      api.zones.list(),
      api.desks.list(),
    ]);

    companies.value = fetchedCompanies;
    buildings.value = fetchedBuildings;
    zones.value = fetchedZones;
    desks.value = fetchedDesks;

    if (companies.value.length > 0 && !buildingForm.value.company_id) {
      buildingForm.value.company_id = companies.value[0].id;
    }

    if (buildings.value.length > 0 && newZoneForm.value.building_id === null) {
      newZoneForm.value.building_id = buildings.value[0].id;
    }

    if (zones.value.length > 0 && !zones.value.some((z) => z.id === benchForm.value.zone_id)) {
      benchForm.value.zone_id = zones.value[0].id;
    }
    if (zones.value.length > 0 && !zones.value.some((z) => z.id === roomForm.value.zone_id)) {
      roomForm.value.zone_id = zones.value[0].id;
    }
  } catch {
    // ignore
  } finally {
    isLoading.value = false;
  }
}

// ==========================================
// Building CRUD Actions
// ==========================================
function openCreateBuildingModal() {
  editingBuilding.value = null;
  buildingError.value = null;
  buildingForm.value = {
    name: '',
    code: '',
    company_id: companies.value.length > 0 ? companies.value[0].id : null,
    address: '',
    city: '',
    total_floors: 10,
  };
  showBuildingModal.value = true;
}

function openEditBuildingModal(b: Building) {
  editingBuilding.value = b;
  buildingError.value = null;
  buildingForm.value = {
    name: b.name,
    code: b.code,
    company_id: b.company_id || (companies.value.length > 0 ? companies.value[0].id : null),
    address: b.address || '',
    city: b.city || '',
    total_floors: b.total_floors || 10,
  };
  showBuildingModal.value = true;
}

async function handleSaveBuilding() {
  isSavingBuilding.value = true;
  buildingError.value = null;

  try {
    if (editingBuilding.value) {
      await api.buildings.update(editingBuilding.value.id, {
        name: buildingForm.value.name,
        company_id: buildingForm.value.company_id,
        address: buildingForm.value.address,
        city: buildingForm.value.city,
        total_floors: buildingForm.value.total_floors,
      });
    } else {
      await api.buildings.create({
        name: buildingForm.value.name,
        code: buildingForm.value.code.toUpperCase().trim(),
        company_id: buildingForm.value.company_id,
        address: buildingForm.value.address,
        city: buildingForm.value.city,
        total_floors: buildingForm.value.total_floors,
      });
    }
    showBuildingModal.value = false;
    await loadData();
  } catch (err: any) {
    if (err.code === 'BUILDING_CODE_EXISTS') {
      buildingError.value = 'Código do edifício já está em uso.';
    } else {
      buildingError.value = err.message || 'Falha ao salvar edifício.';
    }
  } finally {
    isSavingBuilding.value = false;
  }
}

function confirmDeleteBuilding(b: Building) {
  buildingToDelete.value = b;
  deleteBuildingError.value = null;
}

async function handleDeleteBuilding() {
  if (!buildingToDelete.value) return;
  isDeletingBuilding.value = true;
  deleteBuildingError.value = null;

  try {
    await api.buildings.delete(buildingToDelete.value.id);
    buildingToDelete.value = null;
    await loadData();
  } catch (err: any) {
    if (err.code === 'BUILDING_HAS_ZONES') {
      deleteBuildingError.value =
        'Não é possível remover edifício com pavimentos ou andares vinculados. Remova os pavimentos primeiro.';
    } else {
      deleteBuildingError.value = err.message || 'Falha ao remover edifício.';
    }
  } finally {
    isDeletingBuilding.value = false;
  }
}

// ==========================================
// Company Quick Create Action
// ==========================================
async function handleCreateCompany() {
  isCreatingCompany.value = true;
  companyError.value = null;

  try {
    const created = await api.companies.create({
      name: companyForm.value.name,
      code: companyForm.value.code.toUpperCase().trim(),
      cnpj: companyForm.value.cnpj || null,
      description: companyForm.value.description || null,
    });
    showCompanyModal.value = false;
    companyForm.value = { name: '', code: '', cnpj: '', description: '' };
    await loadData();
    buildingForm.value.company_id = created.id;
  } catch (err: any) {
    if (err.code === 'COMPANY_CODE_EXISTS') {
      companyError.value = 'Código da empresa já cadastrado.';
    } else {
      companyError.value = err.message || 'Falha ao cadastrar empresa.';
    }
  } finally {
    isCreatingCompany.value = false;
  }
}

// ==========================================
// Zone / Floor CRUD Actions
// ==========================================
function openCreateZoneModal() {
  editingZone.value = null;
  zoneError.value = null;
  newZoneForm.value = {
    building_id: selectedBuildingFilter.value || (buildings.value[0]?.id ?? null),
    floor: (availableFloors.value[availableFloors.value.length - 1] || 1) + 1,
    name: '',
    description: '',
  };
  showNewZoneModal.value = true;
}

function openEditZoneModal(z: Zone) {
  editingZone.value = z;
  zoneError.value = null;
  newZoneForm.value = {
    building_id: z.building_id ?? (buildings.value[0]?.id ?? null),
    floor: z.floor,
    name: z.name,
    description: z.description || '',
  };
  showNewZoneModal.value = true;
}

async function handleSaveZone() {
  isCreatingZone.value = true;
  zoneError.value = null;

  try {
    if (editingZone.value) {
      await api.zones.update(editingZone.value.id, {
        building_id: newZoneForm.value.building_id,
        floor: newZoneForm.value.floor,
        name: newZoneForm.value.name,
        description: newZoneForm.value.description,
      });
    } else {
      await api.zones.create({
        building_id: newZoneForm.value.building_id,
        name: newZoneForm.value.name,
        floor: newZoneForm.value.floor,
        description: newZoneForm.value.description,
      });
    }
    showNewZoneModal.value = false;
    await loadData();
  } catch (err: any) {
    if (err.code === 'ZONE_NAME_EXISTS') {
      zoneError.value = 'Já existe um setor com este nome.';
    } else {
      zoneError.value = err.message || 'Falha ao salvar pavimento.';
    }
  } finally {
    isCreatingZone.value = false;
  }
}

function confirmDeleteZone(z: Zone) {
  zoneToDelete.value = z;
  deleteZoneError.value = null;
}

async function handleDeleteZone() {
  if (!zoneToDelete.value) return;
  isDeletingZone.value = true;
  deleteZoneError.value = null;

  try {
    await api.zones.delete(zoneToDelete.value.id);
    zoneToDelete.value = null;
    await loadData();
  } catch (err: any) {
    if (err.code === 'ZONE_HAS_DESKS') {
      deleteZoneError.value =
        'Não é possível remover pavimento que possui baias ou salas cadastradas. Remova as baias primeiro.';
    } else {
      deleteZoneError.value = err.message || 'Falha ao remover pavimento.';
    }
  } finally {
    isDeletingZone.value = false;
  }
}

// ==========================================
// Desk CRUD Actions
// ==========================================
function openEditDeskModal(d: Desk) {
  editingDesk.value = d;
  editDeskError.value = null;
  editDeskForm.value = {
    code: d.code,
    zone_id: d.zone_id,
    space_type: d.space_type || 'BAIA',
    capacity: d.capacity || 1,
    required_role: d.required_role || '',
    max_duration_minutes: d.max_duration_minutes ?? null,
    has_monitor: d.has_monitor,
    has_docking_station: d.has_docking_station,
    is_standing_desk: d.is_standing_desk,
  };
}

async function handleUpdateDesk() {
  if (!editingDesk.value) return;
  isUpdatingDesk.value = true;
  editDeskError.value = null;

  try {
    await api.desks.update(editingDesk.value.id, {
      code: editDeskForm.value.code,
      zone_id: editDeskForm.value.zone_id,
      space_type: editDeskForm.value.space_type,
      capacity: editDeskForm.value.capacity,
      required_role: editDeskForm.value.required_role || null,
      max_duration_minutes: editDeskForm.value.max_duration_minutes,
      has_monitor: editDeskForm.value.has_monitor,
      has_docking_station: editDeskForm.value.has_docking_station,
      is_standing_desk: editDeskForm.value.is_standing_desk,
    });
    editingDesk.value = null;
    await loadData();
  } catch (err: any) {
    if (err.code === 'DESK_CODE_EXISTS') {
      editDeskError.value = 'Código da baia já cadastrado.';
    } else {
      editDeskError.value = err.message || 'Falha ao atualizar baia.';
    }
  } finally {
    isUpdatingDesk.value = false;
  }
}

function confirmDeleteDesk(desk: Desk) {
  deskToDelete.value = desk;
  deleteError.value = null;
}

async function handleDeleteDesk() {
  if (!deskToDelete.value) return;
  isDeleting.value = true;
  deleteError.value = null;

  try {
    await api.desks.delete(deskToDelete.value.id);
    if (selectedDeskForQr.value?.id === deskToDelete.value.id) {
      selectedDeskForQr.value = null;
    }
    deskToDelete.value = null;
    await loadData();
  } catch (err: any) {
    if (err.code === 'ACTIVE_BOOKINGS_EXIST') {
      deleteError.value =
        'Esta baia possui reservas ativas em andamento. Cancele as reservas ativas antes de remover.';
    } else {
      deleteError.value = err.message || 'Falha ao remover baia.';
    }
  } finally {
    isDeleting.value = false;
  }
}

// Desk Release (Admin force-cancellation / early checkout)
const deskToRelease = ref<Desk | null>(null);
const isReleasing = ref(false);
const releaseError = ref<string | null>(null);

function confirmReleaseDesk(desk: Desk) {
  deskToRelease.value = desk;
  releaseError.value = null;
}

async function handleReleaseDesk() {
  if (!deskToRelease.value) return;
  isReleasing.value = true;
  releaseError.value = null;

  try {
    await api.desks.release(deskToRelease.value.id);
    if (selectedDeskForQr.value?.id === deskToRelease.value.id) {
      selectedDeskForQr.value = null;
    }
    deskToRelease.value = null;
    await loadData();
  } catch (err: any) {
    releaseError.value = err.message || 'Falha ao liberar baia.';
  } finally {
    isReleasing.value = false;
  }
}

// Helpers for Assistants
function handleSpaceTypeChange(type: SpaceType) {
  roomForm.value.space_type = type;
  if (type === 'SALA_REUNIAO') {
    roomForm.value.capacity = 6;
    roomForm.value.max_duration_minutes = 60;
    roomForm.value.code = `SALA-${filteredDesks.value.length + 1}`;
  } else if (type === 'CABINE_FOCUS') {
    roomForm.value.capacity = 1;
    roomForm.value.max_duration_minutes = 30;
    roomForm.value.required_role = '';
    roomForm.value.code = `FOCUS-${filteredDesks.value.length + 1}`;
  } else {
    roomForm.value.capacity = 1;
    roomForm.value.max_duration_minutes = null;
    roomForm.value.required_role = '';
    roomForm.value.code = `BAIA-${filteredDesks.value.length + 1}`;
  }
}

async function handleCreateBatch() {
  isCreatingBatch.value = true;
  batchError.value = null;

  try {
    const payload = previewDesks.value.map((p) => ({
      code: p.code,
      zone_id: benchForm.value.zone_id,
      pos_x: p.pos_x,
      pos_y: p.pos_y,
      pos_z: p.pos_z,
      rotation_y: p.rotation_y,
      has_monitor: benchForm.value.has_monitor,
      has_docking_station: benchForm.value.has_docking_station,
      is_standing_desk: benchForm.value.is_standing_desk,
    }));

    await api.desks.createBatch(payload);
    showCreateModal.value = false;
    await loadData();
  } catch (err: any) {
    batchError.value = err.message || 'Falha ao gerar bancada de baias.';
  } finally {
    isCreatingBatch.value = false;
  }
}

async function handleCreateRoom() {
  isCreatingRoom.value = true;
  roomError.value = null;

  try {
    const targetZone = zones.value.find((z) => z.id === roomForm.value.zone_id);
    const floor = targetZone ? targetZone.floor : 1;
    const sameFloorDesks = desks.value.filter((d) => {
      const z = zones.value.find((zn) => zn.id === d.zone_id);
      return z?.floor === floor;
    });

    const index = sameFloorDesks.length;
    const posX = Number((((index % 6) - 2.5) * 2.4).toFixed(2));
    const posZ = Number(((Math.floor(index / 6) - 1.5) * 2.4).toFixed(2));

    await api.desks.create({
      code: roomForm.value.code.toUpperCase().trim(),
      zone_id: roomForm.value.zone_id,
      space_type: roomForm.value.space_type,
      capacity: roomForm.value.capacity,
      required_role: roomForm.value.required_role || null,
      max_duration_minutes: roomForm.value.max_duration_minutes,
      pos_x: posX,
      pos_y: 0.0,
      pos_z: posZ,
      rotation_y: 0.0,
      has_monitor: roomForm.value.has_monitor,
      has_docking_station: roomForm.value.has_docking_station,
      is_standing_desk: roomForm.value.is_standing_desk,
    });

    showRoomModal.value = false;
    await loadData();
  } catch (err: any) {
    roomError.value = err.message || 'Falha ao cadastrar sala ou cabine especial.';
  } finally {
    isCreatingRoom.value = false;
  }
}

async function handlePlaceDeskOnGrid(rIndex: number, cIndex: number) {
  if (filteredZones.value.length === 0) {
    alert('Crie ou selecione um andar/setor antes de alocar baias.');
    return;
  }

  const targetZone = filteredZones.value[0];
  const posX = Number(((cIndex - (gridCols - 1) / 2) * 2.4).toFixed(2));
  const posZ = Number(((rIndex - (gridRows - 1) / 2) * 2.4).toFixed(2));
  const code = `D-${targetZone.floor}F-R${rIndex + 1}C${cIndex + 1}`;

  isClickPlacing.value = true;
  try {
    await api.desks.create({
      code,
      zone_id: targetZone.id,
      pos_x: posX,
      pos_y: 0.0,
      pos_z: posZ,
      rotation_y: 0.0,
      has_monitor: true,
      has_docking_station: true,
      is_standing_desk: false,
    });
    await loadData();
  } catch (err: any) {
    alert('Erro ao alocar baia na grade: ' + (err.message || err));
  } finally {
    isClickPlacing.value = false;
  }
}

// QR Code Modal Helpers
function openQrModal(desk: Desk) {
  selectedDeskForQr.value = desk;
  copiedHash.value = false;
}

function closeQrModal() {
  selectedDeskForQr.value = null;
  copiedHash.value = false;
}

async function handleDownloadQr(desk: Desk) {
  isDownloadingQr.value = true;
  try {
    await api.desks.downloadQrCode(desk.id, desk.code);
  } catch (err: any) {
    alert('Erro ao baixar QR code: ' + (err.message || err));
  } finally {
    isDownloadingQr.value = false;
  }
}

async function copyHash(hash: string) {
  try {
    await navigator.clipboard.writeText(hash);
    copiedHash.value = true;
    setTimeout(() => {
      copiedHash.value = false;
    }, 2000);
  } catch {
    // fallback
  }
}

function handlePrintSticker() {
  window.print();
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8 space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-ink tracking-tight flex items-center space-x-2">
          <Shield class="w-5 h-5 text-primary" />
          <span>Hub de Facilities & Gestão Predial</span>
        </h2>
        <p class="text-xs text-ink-subtle mt-1">
          Gerenciamento corporativo hierárquico: Empresas, Edifícios, Pavimentos e Estações de Trabalho.
        </p>
      </div>

      <div class="flex items-center space-x-2.5">
        <button
          class="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
          @click="loadData"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
          <span>Atualizar</span>
        </button>

        <button
          v-if="activeTab === 'buildings'"
          class="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
          @click="showCompanyModal = true"
        >
          <Briefcase class="w-3.5 h-3.5 text-primary" />
          <span>+ Nova Empresa</span>
        </button>

        <button
          v-if="activeTab === 'buildings'"
          class="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
          @click="openCreateBuildingModal"
        >
          <Building2 class="w-4 h-4" />
          <span>+ Novo Edifício</span>
        </button>

        <button
          v-if="activeTab === 'floors'"
          class="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
          @click="openCreateZoneModal"
        >
          <Layers class="w-4 h-4" />
          <span>+ Novo Pavimento</span>
        </button>

        <template v-if="activeTab === 'desks'">
          <button
            class="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-400 text-xs font-semibold transition"
            @click="showRoomModal = true"
          >
            <Users class="w-3.5 h-3.5" />
            <span>+ Sala Especial</span>
          </button>

          <button
            class="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
            @click="showCreateModal = true"
          >
            <Sparkles class="w-4 h-4" />
            <span>Assistente de Baias</span>
          </button>
        </template>
      </div>
    </div>

    <!-- Hierarchy Navigation Tabs -->
    <div class="flex items-center space-x-2 border-b border-hairline pb-2">
      <button
        type="button"
        class="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition"
        :class="activeTab === 'buildings' ? 'bg-primary text-white shadow-sm' : 'bg-surface-2 text-ink-subtle hover:text-ink'"
        @click="activeTab = 'buildings'"
      >
        <Building2 class="w-4 h-4" />
        <span>🏢 Edifícios & Sedes ({{ buildings.length }})</span>
      </button>

      <button
        type="button"
        class="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition"
        :class="activeTab === 'floors' ? 'bg-primary text-white shadow-sm' : 'bg-surface-2 text-ink-subtle hover:text-ink'"
        @click="activeTab = 'floors'"
      >
        <Layers class="w-4 h-4" />
        <span>📐 Pavimentos & Andares ({{ zones.length }})</span>
      </button>

      <button
        type="button"
        class="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition"
        :class="activeTab === 'desks' ? 'bg-primary text-white shadow-sm' : 'bg-surface-2 text-ink-subtle hover:text-ink'"
        @click="activeTab = 'desks'"
      >
        <Monitor class="w-4 h-4" />
        <span>🪑 Baias & Salas ({{ desks.length }})</span>
      </button>
    </div>

    <!-- ============================================================ -->
    <!-- TAB 1: EDIFÍCIOS & SEDES -->
    <!-- ============================================================ -->
    <div v-if="activeTab === 'buildings'" class="space-y-4">
      <div class="bg-surface-1 border border-hairline rounded-xl overflow-hidden shadow-xl">
        <div class="px-4 py-3 border-b border-hairline flex items-center justify-between bg-surface-2/40">
          <h3 class="font-bold text-xs uppercase tracking-wider text-ink-muted">
            Prédios e Sedes Cadastradas
          </h3>
          <span class="text-[11px] text-ink-subtle">
            {{ buildings.length }} edifício(s) em {{ companies.length }} empresa(s)
          </span>
        </div>

        <div v-if="buildings.length === 0" class="p-8 text-center text-ink-subtle text-xs">
          Nenhum edifício cadastrado. Clique em "+ Novo Edifício" para criar o primeiro prédio comercial.
        </div>

        <table v-else class="w-full text-left text-xs">
          <thead class="bg-surface-2/60 border-b border-hairline text-ink-muted uppercase font-semibold">
            <tr>
              <th class="px-4 py-3">Código</th>
              <th class="px-4 py-3">Nome do Edifício</th>
              <th class="px-4 py-3">Empresa / Sede</th>
              <th class="px-4 py-3">Localização</th>
              <th class="px-4 py-3 text-center">Pavimentos</th>
              <th class="px-4 py-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-hairline text-ink">
            <tr v-for="b in buildings" :key="b.id" class="hover:bg-surface-2/30 transition">
              <td class="px-4 py-3.5 font-bold font-mono text-primary">
                {{ b.code }}
              </td>
              <td class="px-4 py-3.5 font-bold text-ink">
                {{ b.name }}
              </td>
              <td class="px-4 py-3.5 text-ink-subtle">
                {{ companies.find(c => c.id === b.company_id)?.name || 'Matriz' }}
              </td>
              <td class="px-4 py-3.5 text-ink-subtle">
                <span v-if="b.city || b.address" class="flex items-center space-x-1">
                  <MapPin class="w-3 h-3 text-ink-muted" />
                  <span>{{ b.city ? `${b.city} - ` : '' }}{{ b.address }}</span>
                </span>
                <span v-else class="text-ink-muted italic">Não informado</span>
              </td>
              <td class="px-4 py-3.5 text-center font-bold">
                <span class="px-2 py-0.5 rounded bg-surface-2 border border-hairline text-ink">
                  {{ zones.filter(z => z.building_id === b.id).length }} / {{ b.total_floors }}
                </span>
              </td>
              <td class="px-4 py-3.5 text-right space-x-2">
                <button
                  class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
                  @click="openEditBuildingModal(b)"
                >
                  <Edit3 class="w-3.5 h-3.5 text-ink-subtle" />
                  <span>Editar</span>
                </button>
                <button
                  class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 text-xs transition"
                  @click="confirmDeleteBuilding(b)"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                  <span>Excluir</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- TAB 2: PAVIMENTOS & ANDARES -->
    <!-- ============================================================ -->
    <div v-if="activeTab === 'floors'" class="space-y-4">
      <!-- Building Filter Bar -->
      <div class="bg-surface-1 border border-hairline rounded-xl p-3 shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-center space-x-2">
          <Building2 class="w-4 h-4 text-primary shrink-0" />
          <span class="text-xs font-semibold uppercase tracking-wider text-ink-muted">Filtrar por Edifício:</span>
          <select
            v-model="selectedBuildingFilter"
            class="bg-surface-2 border border-hairline rounded-lg px-3 py-1.5 text-xs text-ink focus:outline-none focus:border-primary"
          >
            <option :value="null">Todos os Edifícios</option>
            <option v-for="b in buildings" :key="b.id" :value="b.id">
              {{ b.name }} ({{ b.code }})
            </option>
          </select>
        </div>

        <span class="text-xs text-ink-subtle">
          Exibindo <strong>{{ filteredZones.length }}</strong> pavimento(s)
        </span>
      </div>

      <div class="bg-surface-1 border border-hairline rounded-xl overflow-hidden shadow-xl">
        <div class="px-4 py-3 border-b border-hairline flex items-center justify-between bg-surface-2/40">
          <h3 class="font-bold text-xs uppercase tracking-wider text-ink-muted">
            Lista de Pavimentos / Andares
          </h3>
        </div>

        <div v-if="filteredZones.length === 0" class="p-8 text-center text-ink-subtle text-xs">
          Nenhum pavimento encontrado. Clique em "+ Novo Pavimento" para cadastrar um andar.
        </div>

        <table v-else class="w-full text-left text-xs">
          <thead class="bg-surface-2/60 border-b border-hairline text-ink-muted uppercase font-semibold">
            <tr>
              <th class="px-4 py-3">Edifício</th>
              <th class="px-4 py-3">Andar</th>
              <th class="px-4 py-3">Nome do Pavimento / Setor</th>
              <th class="px-4 py-3">Descrição</th>
              <th class="px-4 py-3 text-center">Baias Alocadas</th>
              <th class="px-4 py-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-hairline text-ink">
            <tr v-for="z in filteredZones" :key="z.id" class="hover:bg-surface-2/30 transition">
              <td class="px-4 py-3.5">
                <span class="px-2 py-0.5 rounded bg-surface-2 border border-hairline text-ink-subtle font-mono text-[10px]">
                  {{ buildings.find(b => b.id === z.building_id)?.name || 'Edifício Padrão' }}
                </span>
              </td>
              <td class="px-4 py-3.5 font-bold text-ink">
                {{ z.floor }}º Andar
              </td>
              <td class="px-4 py-3.5 font-medium text-ink">
                {{ z.name }}
              </td>
              <td class="px-4 py-3.5 text-ink-subtle">
                {{ z.description || '—' }}
              </td>
              <td class="px-4 py-3.5 text-center font-bold">
                <span class="px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
                  {{ desks.filter(d => d.zone_id === z.id).length }} baias
                </span>
              </td>
              <td class="px-4 py-3.5 text-right space-x-2">
                <button
                  class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
                  @click="openEditZoneModal(z)"
                >
                  <Edit3 class="w-3.5 h-3.5 text-ink-subtle" />
                  <span>Editar</span>
                </button>
                <button
                  class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 text-xs transition"
                  @click="confirmDeleteZone(z)"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                  <span>Excluir</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- TAB 3: BAIAS & SALAS -->
    <!-- ============================================================ -->
    <div v-if="activeTab === 'desks'" class="space-y-6">
      <!-- Building and Floor Selector -->
      <div class="bg-surface-1 border border-hairline rounded-xl p-3 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-3">
          <!-- Building Selector -->
          <div v-if="buildings.length > 0" class="flex items-center space-x-2">
            <Building2 class="w-4 h-4 text-primary shrink-0" />
            <select
              v-model="selectedBuildingFilter"
              class="bg-surface-2 border border-hairline rounded-lg px-2.5 py-1 text-xs text-ink focus:outline-none focus:border-primary"
            >
              <option :value="null">Todos os Edifícios</option>
              <option v-for="b in buildings" :key="b.id" :value="b.id">
                {{ b.name }}
              </option>
            </select>
          </div>

          <!-- Floor Switcher -->
          <div class="flex items-center space-x-1 bg-surface-2 p-1 rounded-lg border border-hairline overflow-x-auto">
            <button
              v-for="fl in availableFloors"
              :key="fl"
              type="button"
              class="px-3 py-1 text-xs font-semibold rounded-md transition whitespace-nowrap"
              :class="selectedFloor === fl ? 'bg-primary text-white shadow-sm' : 'text-ink-subtle hover:text-ink'"
              @click="selectedFloor = fl"
            >
              {{ fl }}º Andar
            </button>
            <button
              type="button"
              class="px-3 py-1 text-xs font-semibold rounded-md transition whitespace-nowrap"
              :class="selectedFloor === null ? 'bg-primary text-white shadow-sm' : 'text-ink-subtle hover:text-ink'"
              @click="selectedFloor = null"
            >
              Todos os Andares
            </button>
          </div>
        </div>

        <!-- Quick Metrics -->
        <div class="flex items-center space-x-3 text-xs text-ink-subtle">
          <span>Baias: <strong class="text-ink">{{ filteredDesks.length }}</strong></span>
          <span>•</span>
          <span class="text-emerald-400">Livres: <strong>{{ filteredDesks.filter(d => d.status === 'DISPONIVEL').length }}</strong></span>
          <span>•</span>
          <span class="text-primary">Ocupadas: <strong>{{ filteredDesks.filter(d => d.status === 'OCUPADA').length }}</strong></span>
        </div>
      </div>

      <!-- Interactive Floorplan Grid Preview (Click-to-Place) -->
      <div class="bg-surface-1 border border-hairline rounded-xl p-5 shadow-xl space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <MousePointerClick class="w-4 h-4 text-emerald-400" />
            <h3 class="font-bold text-sm text-ink">Planta Interativa do Andar (Clique no espaço vazio para criar baia)</h3>
          </div>
          <span class="text-[11px] text-ink-subtle">
            💡 Clique em qualquer célula vazia para posicionar uma estação automaticamente.
          </span>
        </div>

        <!-- Grid Matrix -->
        <div class="bg-surface-2/60 border border-hairline rounded-xl p-4 overflow-x-auto">
          <div class="grid grid-cols-6 gap-2.5 min-w-[600px]">
            <template v-for="r in gridRows" :key="`row-${r}`">
              <template v-for="c in gridCols" :key="`cell-${r}-${c}`">
                <!-- Occupied Cell with Desk or Room -->
                <div
                  v-if="getDeskAtGridCell(r - 1, c - 1)"
                  class="bg-surface-3/90 border rounded-lg p-2 flex flex-col justify-between h-16 shadow-sm relative group cursor-pointer transition"
                  :class="{
                    'border-purple-500/60 bg-purple-500/10': getDeskAtGridCell(r - 1, c - 1)?.space_type === 'SALA_REUNIAO',
                    'border-cyan-500/60 bg-cyan-500/10': getDeskAtGridCell(r - 1, c - 1)?.space_type === 'CABINE_FOCUS',
                    'border-primary/40': !getDeskAtGridCell(r - 1, c - 1)?.space_type || getDeskAtGridCell(r - 1, c - 1)?.space_type === 'BAIA',
                  }"
                  @click="openQrModal(getDeskAtGridCell(r - 1, c - 1)!)"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-1 overflow-hidden">
                      <span class="font-bold text-ink text-xs truncate">{{ getDeskAtGridCell(r - 1, c - 1)?.code }}</span>
                      <Lock v-if="getDeskAtGridCell(r - 1, c - 1)?.required_role" class="w-2.5 h-2.5 text-amber-400 shrink-0" />
                    </div>
                    <span
                      class="w-2 h-2 rounded-full shrink-0"
                      :class="{
                        'bg-emerald-400': getDeskAtGridCell(r - 1, c - 1)?.status === 'DISPONIVEL',
                        'bg-primary': getDeskAtGridCell(r - 1, c - 1)?.status === 'OCUPADA',
                        'bg-amber-400': getDeskAtGridCell(r - 1, c - 1)?.status === 'RESERVADA',
                      }"
                    />
                  </div>
                  <div class="flex items-center justify-between text-[10px] text-ink-subtle">
                    <span class="flex items-center space-x-1">
                      <Users v-if="getDeskAtGridCell(r - 1, c - 1)?.space_type === 'SALA_REUNIAO'" class="w-3 h-3 text-purple-400" />
                      <Headphones v-else-if="getDeskAtGridCell(r - 1, c - 1)?.space_type === 'CABINE_FOCUS'" class="w-3 h-3 text-cyan-400" />
                      <Monitor v-else class="w-3 h-3 text-primary" />
                      <span>{{ getDeskAtGridCell(r - 1, c - 1)?.space_type === 'SALA_REUNIAO' ? 'Sala' : (getDeskAtGridCell(r - 1, c - 1)?.space_type === 'CABINE_FOCUS' ? 'Cabine' : 'Baia') }}</span>
                    </span>
                    <span class="group-hover:text-primary transition font-medium">Ver QR</span>
                  </div>
                </div>

                <!-- Empty Clickable Cell -->
                <button
                  v-else
                  type="button"
                  :disabled="isClickPlacing"
                  class="border border-dashed border-hairline/80 hover:border-emerald-500/60 hover:bg-emerald-500/5 rounded-lg p-2 flex flex-col items-center justify-center h-16 transition group text-ink-subtle hover:text-emerald-400"
                  title="Clique para criar baia nesta posição"
                  @click="handlePlaceDeskOnGrid(r - 1, c - 1)"
                >
                  <Plus class="w-4 h-4 text-ink-subtle group-hover:text-emerald-400 group-hover:scale-125 transition" />
                  <span class="text-[10px] mt-1 text-ink-subtle group-hover:text-ink">+ Alocar</span>
                </button>
              </template>
            </template>
          </div>
        </div>
      </div>

      <!-- Desks Table -->
      <div class="bg-surface-1 border border-hairline rounded-xl overflow-hidden shadow-xl">
        <div class="px-4 py-3 border-b border-hairline flex items-center justify-between bg-surface-2/40">
          <h3 class="font-bold text-xs uppercase tracking-wider text-ink-muted">
            Listagem de Baias & QR Codes ({{ filteredDesks.length }})
          </h3>
          <span class="text-[11px] text-ink-subtle">
            Exibindo {{ selectedFloor ? `Andar ${selectedFloor}` : 'Todos os Andares' }}
          </span>
        </div>

        <table class="w-full text-left text-xs">
          <thead class="bg-surface-2/60 border-b border-hairline text-ink-muted uppercase font-semibold">
            <tr>
              <th class="px-4 py-3">Código</th>
              <th class="px-4 py-3">Tipo / Capacidade</th>
              <th class="px-4 py-3">Andar / Setor</th>
              <th class="px-4 py-3">Políticas de Acesso & Tempo</th>
              <th class="px-4 py-3">Equipamentos</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-hairline text-ink">
            <tr v-for="d in filteredDesks" :key="d.id" class="hover:bg-surface-2/30 transition">
              <td class="px-4 py-3.5 font-bold text-ink">
                {{ d.code }}
              </td>
              <td class="px-4 py-3.5">
                <span
                  v-if="d.space_type === 'SALA_REUNIAO'"
                  class="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-purple-500/15 text-purple-400 border border-purple-500/30 font-bold text-[10px]"
                >
                  <Users class="w-3 h-3" />
                  <span>Sala Reunião ({{ d.capacity || 4 }}p)</span>
                </span>
                <span
                  v-else-if="d.space_type === 'CABINE_FOCUS'"
                  class="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 font-bold text-[10px]"
                >
                  <Headphones class="w-3 h-3" />
                  <span>Cabine Focus</span>
                </span>
                <span
                  v-else
                  class="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-surface-2 text-ink-subtle border border-hairline text-[10px]"
                >
                  <Monitor class="w-3 h-3" />
                  <span>Baia Individual</span>
                </span>
              </td>
              <td class="px-4 py-3.5 text-ink-muted">
                {{ zones.find(z => z.id === d.zone_id)?.name || `Zona #${d.zone_id}` }}
              </td>
              <td class="px-4 py-3.5">
                <div class="flex flex-col space-y-0.5">
                  <div class="flex items-center space-x-1 text-[11px]">
                    <span v-if="d.required_role === 'gestor'" class="text-amber-400 font-semibold flex items-center space-x-0.5">
                      <Lock class="w-3 h-3" />
                      <span>Restrito: Gestor</span>
                    </span>
                    <span v-else class="text-emerald-400 font-medium">Livre p/ Todos</span>
                  </div>
                  <div class="text-[10px] text-ink-subtle flex items-center space-x-1">
                    <Clock class="w-3 h-3" />
                    <span>{{ d.max_duration_minutes ? `Máx ${d.max_duration_minutes >= 60 ? `${d.max_duration_minutes / 60}h` : `${d.max_duration_minutes}m`}` : 'Sem limite' }}</span>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3.5">
                <div class="flex items-center space-x-2 text-ink-subtle">
                  <span v-if="d.has_monitor" class="text-primary font-medium">Monitor Duplo</span>
                  <span v-if="d.has_docking_station">• Dock USB-C</span>
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
              <td class="px-4 py-3.5 text-right space-x-2">
                <button
                  v-if="d.status === 'RESERVADA' || d.status === 'OCUPADA'"
                  class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-xs font-semibold transition"
                  title="Liberar baia e cancelar reserva ativa imediatamente"
                  @click="confirmReleaseDesk(d)"
                >
                  <LogOut class="w-3.5 h-3.5" />
                  <span>Liberar</span>
                </button>
                <button
                  class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
                  title="Editar configurações da baia"
                  @click="openEditDeskModal(d)"
                >
                  <Edit3 class="w-3.5 h-3.5 text-ink-subtle" />
                  <span>Editar</span>
                </button>
                <button
                  class="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs transition"
                  title="Visualizar adesivo e imprimir"
                  @click="openQrModal(d)"
                >
                  <QrCode class="w-3.5 h-3.5 text-primary" />
                  <span>QR</span>
                </button>
                <button
                  class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-primary/10 hover:bg-primary/20 border border-primary/30 text-primary text-xs font-medium transition"
                  title="Baixar PNG do QR Code"
                  :disabled="isDownloadingQr"
                  @click="handleDownloadQr(d)"
                >
                  <Download class="w-3.5 h-3.5" />
                  <span>PNG</span>
                </button>
                <button
                  class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 hover:border-red-500/40 text-red-400 text-xs font-medium transition"
                  title="Remover baia/sala"
                  @click="confirmDeleteDesk(d)"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                  <span>Excluir</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: NOVO / EDITAR EDIFÍCIO -->
    <!-- ============================================================ -->
    <div
      v-if="showBuildingModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Building2 class="w-5 h-5 text-primary" />
            <h3 class="font-bold text-ink text-sm">
              {{ editingBuilding ? 'Editar Edifício' : 'Cadastrar Novo Edifício' }}
            </h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="showBuildingModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-3" @submit.prevent="handleSaveBuilding">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Empresa / Sede Proprietária</label>
            <select
              v-model="buildingForm.company_id"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            >
              <option v-for="c in companies" :key="c.id" :value="c.id">
                {{ c.name }} ({{ c.code }})
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Nome do Edifício</label>
              <input
                v-model="buildingForm.name"
                type="text"
                required
                placeholder="Ex: Nexus Tower"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Código Único (Slug)</label>
              <input
                v-model="buildingForm.code"
                type="text"
                :disabled="!!editingBuilding"
                required
                placeholder="Ex: NEXUS-SP"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink uppercase focus:outline-none focus:border-primary disabled:opacity-50"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Cidade</label>
              <input
                v-model="buildingForm.city"
                type="text"
                placeholder="Ex: São Paulo"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Total de Andares</label>
              <input
                v-model.number="buildingForm.total_floors"
                type="number"
                min="1"
                max="120"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Endereço Completo</label>
            <input
              v-model="buildingForm.address"
              type="text"
              placeholder="Ex: Av. Paulista, 1000 - Bela Vista"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div v-if="buildingError" class="p-2.5 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
            {{ buildingError }}
          </div>

          <button
            type="submit"
            :disabled="isSavingBuilding"
            class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            {{ isSavingBuilding ? 'Salvando...' : (editingBuilding ? 'Atualizar Edifício' : 'Criar Edifício') }}
          </button>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: NOVA EMPRESA -->
    <!-- ============================================================ -->
    <div
      v-if="showCompanyModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Briefcase class="w-5 h-5 text-primary" />
            <h3 class="font-bold text-ink text-sm">Cadastrar Nova Empresa</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="showCompanyModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-3" @submit.prevent="handleCreateCompany">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Razão Social / Nome Fantasia</label>
            <input
              v-model="companyForm.name"
              type="text"
              required
              placeholder="Ex: TechCorp Global S.A."
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Código Único (Slug)</label>
              <input
                v-model="companyForm.code"
                type="text"
                required
                placeholder="Ex: TECHCORP"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink uppercase focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">CNPJ (Opcional)</label>
              <input
                v-model="companyForm.cnpj"
                type="text"
                placeholder="00.000.000/0001-00"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Descrição</label>
            <textarea
              v-model="companyForm.description"
              rows="2"
              placeholder="Ex: Matriz corporativa e subsidiárias de tecnologia"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div v-if="companyError" class="p-2.5 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
            {{ companyError }}
          </div>

          <button
            type="submit"
            :disabled="isCreatingCompany"
            class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            {{ isCreatingCompany ? 'Cadastrando...' : 'Cadastrar Empresa' }}
          </button>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: CONFIRMAR EXCLUSÃO DE EDIFÍCIO -->
    <!-- ============================================================ -->
    <div
      v-if="buildingToDelete"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Trash2 class="w-5 h-5 text-red-400" />
            <h3 class="font-bold text-ink text-sm">Confirmar Exclusão de Edifício</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="buildingToDelete = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-3">
          <p class="text-xs text-ink-muted">
            Tem certeza que deseja remover o edifício <strong class="text-ink text-sm">{{ buildingToDelete.name }}</strong> ({{ buildingToDelete.code }})?
          </p>

          <div
            v-if="deleteBuildingError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ deleteBuildingError }}</span>
          </div>
        </div>

        <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
            @click="buildingToDelete = null"
          >
            Cancelar
          </button>
          <button
            type="button"
            :disabled="isDeletingBuilding"
            class="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            @click="handleDeleteBuilding"
          >
            <Trash2 class="w-3.5 h-3.5" />
            <span>{{ isDeletingBuilding ? 'Removendo...' : 'Sim, Excluir Edifício' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: NOVO / EDITAR PAVIMENTO / ANDAR -->
    <!-- ============================================================ -->
    <div
      v-if="showNewZoneModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Layers class="w-5 h-5 text-primary" />
            <h3 class="font-bold text-ink text-sm">
              {{ editingZone ? 'Editar Pavimento / Andar' : 'Adicionar Pavimento ao Edifício' }}
            </h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="showNewZoneModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-3" @submit.prevent="handleSaveZone">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Edifício Vinculado</label>
            <select
              v-model="newZoneForm.building_id"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            >
              <option :value="null">Edifício Geral / Padrão</option>
              <option v-for="b in buildings" :key="b.id" :value="b.id">
                {{ b.name }} ({{ b.code }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Número do Andar</label>
            <input
              v-model.number="newZoneForm.floor"
              type="number"
              min="0"
              max="120"
              required
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Nome do Setor / Pavimento</label>
            <input
              v-model="newZoneForm.name"
              type="text"
              required
              placeholder="Ex: 4º Andar - Squads de Engenharia"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Descrição (opcional)</label>
            <textarea
              v-model="newZoneForm.description"
              rows="2"
              placeholder="Ex: Espaço colaborativo com 20 baias e salas de reunião"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-ink focus:outline-none focus:border-primary"
            />
          </div>

          <div v-if="zoneError" class="p-2.5 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
            {{ zoneError }}
          </div>

          <button
            type="submit"
            :disabled="isCreatingZone"
            class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            {{ isCreatingZone ? 'Salvando...' : (editingZone ? 'Atualizar Pavimento' : 'Cadastrar Pavimento') }}
          </button>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: CONFIRMAR EXCLUSÃO DE PAVIMENTO -->
    <!-- ============================================================ -->
    <div
      v-if="zoneToDelete"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Trash2 class="w-5 h-5 text-red-400" />
            <h3 class="font-bold text-ink text-sm">Confirmar Exclusão de Pavimento</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="zoneToDelete = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-3">
          <p class="text-xs text-ink-muted">
            Tem certeza que deseja remover o pavimento <strong class="text-ink text-sm">{{ zoneToDelete.name }}</strong> ({{ zoneToDelete.floor }}º Andar)?
          </p>

          <div
            v-if="deleteZoneError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ deleteZoneError }}</span>
          </div>
        </div>

        <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
            @click="zoneToDelete = null"
          >
            Cancelar
          </button>
          <button
            type="button"
            :disabled="isDeletingZone"
            class="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            @click="handleDeleteZone"
          >
            <Trash2 class="w-3.5 h-3.5" />
            <span>{{ isDeletingZone ? 'Removendo...' : 'Sim, Excluir Pavimento' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: EDITAR BAIA / SALA -->
    <!-- ============================================================ -->
    <div
      v-if="editingDesk"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Edit3 class="w-5 h-5 text-primary" />
            <h3 class="font-bold text-ink text-sm">Editar Estação / Sala ({{ editingDesk.code }})</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="editingDesk = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleUpdateDesk">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Código da Baia</label>
              <input
                v-model="editDeskForm.code"
                type="text"
                required
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink uppercase focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Pavimento / Andar</label>
              <select
                v-model="editDeskForm.zone_id"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              >
                <option v-for="z in zones" :key="z.id" :value="z.id">
                  {{ z.name }} (Andar {{ z.floor }})
                </option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2">
            <button
              type="button"
              class="p-2.5 rounded-lg border text-center transition flex flex-col items-center justify-center space-y-1"
              :class="editDeskForm.space_type === 'SALA_REUNIAO' ? 'bg-purple-500/15 border-purple-500/60 text-purple-300' : 'bg-surface-2 border-hairline text-ink-subtle hover:text-ink'"
              @click="editDeskForm.space_type = 'SALA_REUNIAO'"
            >
              <Users class="w-4 h-4" />
              <span class="text-xs font-bold">Sala Reunião</span>
            </button>
            <button
              type="button"
              class="p-2.5 rounded-lg border text-center transition flex flex-col items-center justify-center space-y-1"
              :class="editDeskForm.space_type === 'CABINE_FOCUS' ? 'bg-cyan-500/15 border-cyan-500/60 text-cyan-300' : 'bg-surface-2 border-hairline text-ink-subtle hover:text-ink'"
              @click="editDeskForm.space_type = 'CABINE_FOCUS'"
            >
              <Headphones class="w-4 h-4" />
              <span class="text-xs font-bold">Cabine Focus</span>
            </button>
            <button
              type="button"
              class="p-2.5 rounded-lg border text-center transition flex flex-col items-center justify-center space-y-1"
              :class="editDeskForm.space_type === 'BAIA' ? 'bg-primary/15 border-primary/60 text-primary' : 'bg-surface-2 border-hairline text-ink-subtle hover:text-ink'"
              @click="editDeskForm.space_type = 'BAIA'"
            >
              <Monitor class="w-4 h-4" />
              <span class="text-xs font-bold">Baia Individual</span>
            </button>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Capacidade (Pessoas)</label>
              <input
                v-model.number="editDeskForm.capacity"
                type="number"
                min="1"
                max="50"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Duração Máxima</label>
              <select
                v-model="editDeskForm.max_duration_minutes"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              >
                <option :value="null">Sem limite (dia todo)</option>
                <option :value="30">30 minutos (Express)</option>
                <option :value="60">1 hora</option>
                <option :value="120">2 horas</option>
                <option :value="240">4 horas</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2 pt-1 text-xs text-ink-muted">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="editDeskForm.has_monitor" type="checkbox" class="accent-primary" />
              <span>Monitor</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="editDeskForm.has_docking_station" type="checkbox" class="accent-primary" />
              <span>Docking</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="editDeskForm.is_standing_desk" type="checkbox" class="accent-primary" />
              <span>Standing</span>
            </label>
          </div>

          <div v-if="editDeskError" class="p-2.5 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
            {{ editDeskError }}
          </div>

          <button
            type="submit"
            :disabled="isUpdatingDesk"
            class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            {{ isUpdatingDesk ? 'Salvando...' : 'Salvar Alterações' }}
          </button>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: ASSISTENTE INTELIGENTE DE BANCADAS (ROW BUILDER) -->
    <!-- ============================================================ -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-5">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Sparkles class="w-5 h-5 text-primary" />
            <div>
              <h3 class="font-bold text-ink text-sm">Assistente Inteligente de Bancadas</h3>
              <p class="text-[11px] text-ink-subtle">Crie conjuntos inteiros de baias perfeitamente alinhadas sem digitar coordenadas.</p>
            </div>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="showCreateModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleCreateBatch">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Andar / Setor de Destino</label>
            <select
              v-model="benchForm.zone_id"
              class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
            >
              <option v-for="z in zones" :key="z.id" :value="z.id">
                {{ z.name }} (Andar {{ z.floor }})
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Identificador da Bancada</label>
              <input
                v-model="benchForm.prefix"
                type="text"
                required
                placeholder="Ex: B, C, ENG"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink uppercase focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Quantidade de Baias</label>
              <div class="flex items-center space-x-1.5">
                <button
                  v-for="n in [2, 4, 6]"
                  :key="n"
                  type="button"
                  class="flex-1 py-1.5 text-xs font-semibold rounded-md border transition"
                  :class="benchForm.count === n ? 'bg-primary text-white border-primary' : 'bg-surface-2 border-hairline text-ink-subtle hover:text-ink'"
                  @click="benchForm.count = n"
                >
                  {{ n }}
                </button>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1">Configuração Espacial</label>
            <div class="grid grid-cols-2 gap-2">
              <button
                type="button"
                class="p-2.5 rounded-lg border text-left transition"
                :class="benchForm.layout === 'face-to-face' ? 'bg-primary/10 border-primary text-ink' : 'bg-surface-2 border-hairline text-ink-subtle'"
                @click="benchForm.layout = 'face-to-face'"
              >
                <p class="text-xs font-bold text-ink">Frente a Frente</p>
                <p class="text-[10px] text-ink-subtle">Coworking moderno (0° e 180°)</p>
              </button>

              <button
                type="button"
                class="p-2.5 rounded-lg border text-left transition"
                :class="benchForm.layout === 'single-row' ? 'bg-primary/10 border-primary text-ink' : 'bg-surface-2 border-hairline text-ink-subtle'"
                @click="benchForm.layout = 'single-row'"
              >
                <p class="text-xs font-bold text-ink">Fileira Única</p>
                <p class="text-[10px] text-ink-subtle">Voltadas para janela/parede</p>
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 pt-1 text-xs text-ink-muted">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="benchForm.has_monitor" type="checkbox" class="accent-primary" />
              <span>Monitores Duplos</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="benchForm.has_docking_station" type="checkbox" class="accent-primary" />
              <span>Docking USB-C</span>
            </label>
          </div>

          <div class="p-3 bg-surface-2/80 rounded-xl border border-hairline space-y-2">
            <p class="text-[11px] font-semibold text-ink-muted">Pré-visualização do Lote:</p>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="p in previewDesks"
                :key="p.code"
                class="px-2 py-1 rounded bg-surface-1 border border-hairline text-[11px] font-mono font-bold text-primary"
              >
                {{ p.code }}
              </span>
            </div>
            <p class="text-[10px] text-ink-subtle">
              Coordenadas 3D e espaçamento ergonômico serão gerados automaticamente.
            </p>
          </div>

          <div v-if="batchError" class="p-2.5 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
            {{ batchError }}
          </div>

          <button
            type="submit"
            :disabled="isCreatingBatch"
            class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            {{ isCreatingBatch ? 'Gerando...' : `Criar Bancada com ${benchForm.count} Baias` }}
          </button>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: NOVA SALA OU ESPAÇO ESPECIAL -->
    <!-- ============================================================ -->
    <div
      v-if="showRoomModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Users class="w-5 h-5 text-purple-400" />
            <div>
              <h3 class="font-bold text-ink text-sm">Cadastrar Sala ou Espaço Especial</h3>
              <p class="text-[11px] text-ink-subtle">Configure salas de reunião ou cabines com políticas de acesso e duração máxima.</p>
            </div>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="showRoomModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleCreateRoom">
          <div>
            <label class="block text-xs font-medium text-ink-muted mb-1.5">Tipo de Espaço</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                type="button"
                class="p-2.5 rounded-lg border text-center transition flex flex-col items-center justify-center space-y-1"
                :class="roomForm.space_type === 'SALA_REUNIAO' ? 'bg-purple-500/15 border-purple-500/60 text-purple-300' : 'bg-surface-2 border-hairline text-ink-subtle hover:text-ink'"
                @click="handleSpaceTypeChange('SALA_REUNIAO')"
              >
                <Users class="w-4 h-4" />
                <span class="text-xs font-bold">Sala de Reunião</span>
              </button>
              <button
                type="button"
                class="p-2.5 rounded-lg border text-center transition flex flex-col items-center justify-center space-y-1"
                :class="roomForm.space_type === 'CABINE_FOCUS' ? 'bg-cyan-500/15 border-cyan-500/60 text-cyan-300' : 'bg-surface-2 border-hairline text-ink-subtle hover:text-ink'"
                @click="handleSpaceTypeChange('CABINE_FOCUS')"
              >
                <Headphones class="w-4 h-4" />
                <span class="text-xs font-bold">Cabine Focus</span>
              </button>
              <button
                type="button"
                class="p-2.5 rounded-lg border text-center transition flex flex-col items-center justify-center space-y-1"
                :class="roomForm.space_type === 'BAIA' ? 'bg-primary/15 border-primary/60 text-primary' : 'bg-surface-2 border-hairline text-ink-subtle hover:text-ink'"
                @click="handleSpaceTypeChange('BAIA')"
              >
                <Monitor class="w-4 h-4" />
                <span class="text-xs font-bold">Baia Individual</span>
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Andar / Setor</label>
              <select
                v-model="roomForm.zone_id"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              >
                <option v-for="z in zones" :key="z.id" :value="z.id">
                  {{ z.name }} (Andar {{ z.floor }})
                </option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Identificador / Código</label>
              <input
                v-model="roomForm.code"
                type="text"
                required
                placeholder="Ex: SALA-01"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink uppercase focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Capacidade (Pessoas)</label>
              <input
                v-model.number="roomForm.capacity"
                type="number"
                min="1"
                max="50"
                required
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-ink-muted mb-1">Duração Máxima</label>
              <select
                v-model="roomForm.max_duration_minutes"
                class="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-primary"
              >
                <option :value="null">Sem limite (dia todo)</option>
                <option :value="30">30 minutos (Express)</option>
                <option :value="60">1 hora</option>
                <option :value="120">2 horas</option>
                <option :value="240">4 horas</option>
              </select>
            </div>
          </div>

          <div v-if="roomError" class="p-2.5 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
            {{ roomError }}
          </div>

          <button
            type="submit"
            :disabled="isCreatingRoom"
            class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            {{ isCreatingRoom ? 'Cadastrando...' : 'Cadastrar Espaço Especial' }}
          </button>
        </form>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: EXPORTAR ADESIVO QR CODE FÍSICO COM TOKEN IMUTÁVEL -->
    <!-- ============================================================ -->
    <div
      v-if="selectedDeskForQr"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl overflow-hidden">
        <div class="px-6 py-4 border-b border-hairline flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <QrCode class="w-5 h-5 text-primary" />
            <h3 class="font-bold text-ink text-sm">Exportar & Imprimir Adesivo QR Code</h3>
          </div>
          <button class="p-1 rounded-md text-ink-subtle hover:text-ink hover:bg-surface-3 transition" @click="closeQrModal">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="p-6 space-y-6">
          <div
            id="printable-sticker"
            class="bg-white text-zinc-900 rounded-2xl p-6 shadow-md border-2 border-zinc-200 text-center flex flex-col items-center space-y-3"
          >
            <div class="flex items-center space-x-1.5 text-zinc-500 text-[11px] font-bold tracking-widest uppercase">
              <span>MYALOCA</span>
              <span>•</span>
              <span>ESTAÇÃO DE TRABALHO</span>
            </div>

            <div class="text-3xl font-black tracking-tight text-zinc-950 font-mono">
              {{ selectedDeskForQr.code }}
            </div>

            <div class="p-2 bg-white rounded-xl border border-zinc-200 shadow-inner">
              <img
                :src="api.desks.getQrCodeUrl(selectedDeskForQr.id)"
                :alt="`QR Code da ${selectedDeskForQr.code}`"
                class="w-48 h-48 object-contain"
              />
            </div>

            <p class="text-xs text-zinc-600 font-medium max-w-xs">
              Aponte a câmera do seu dispositivo para validar sua presença física na baia.
            </p>

            <div class="w-full bg-zinc-100 rounded-lg p-2 flex items-center justify-between text-[10px] font-mono text-zinc-600">
              <span class="truncate max-w-[220px]" :title="selectedDeskForQr.qr_code_hash">
                Hash: {{ selectedDeskForQr.qr_code_hash }}
              </span>
              <button
                type="button"
                class="p-1 rounded hover:bg-zinc-200 text-zinc-700 transition"
                title="Copiar Hash"
                @click="copyHash(selectedDeskForQr.qr_code_hash)"
              >
                <Check v-if="copiedHash" class="w-3.5 h-3.5 text-emerald-600" />
                <Copy v-else class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3 pt-2">
            <button
              type="button"
              class="flex items-center justify-center space-x-2 py-2.5 px-4 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
              @click="handlePrintSticker"
            >
              <Printer class="w-4 h-4 text-ink-subtle" />
              <span>Imprimir Adesivo</span>
            </button>

            <button
              type="button"
              :disabled="isDownloadingQr"
              class="flex items-center justify-center space-x-2 py-2.5 px-4 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-sm transition"
              @click="handleDownloadQr(selectedDeskForQr)"
            >
              <Download class="w-4 h-4" />
              <span>{{ isDownloadingQr ? 'Baixando...' : 'Baixar PNG' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: CONFIRMAR EXCLUSÃO DE BAIA -->
    <!-- ============================================================ -->
    <div
      v-if="deskToDelete"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <Trash2 class="w-5 h-5 text-red-400" />
            <h3 class="font-bold text-ink text-sm">Confirmar Exclusão de Estação</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="deskToDelete = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-3">
          <p class="text-xs text-ink-muted">
            Tem certeza que deseja remover a estação <strong class="text-ink text-sm">{{ deskToDelete.code }}</strong> do sistema?
          </p>

          <div
            v-if="deleteError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ deleteError }}</span>
          </div>

          <p class="text-[11px] text-ink-subtle">
            ⚠️ Esta ação removerá a baia da planta 3D, desativará o QR code impresso e apagará registros arquivados.
          </p>
        </div>

        <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
            @click="deskToDelete = null"
          >
            Cancelar
          </button>
          <button
            type="button"
            :disabled="isDeleting"
            class="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            @click="handleDeleteDesk"
          >
            <Trash2 class="w-3.5 h-3.5" />
            <span>{{ isDeleting ? 'Removendo...' : 'Sim, Excluir Estação' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL: CONFIRMAR LIBERAÇÃO DE BAIA -->
    <!-- ============================================================ -->
    <div
      v-if="deskToRelease"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div class="bg-surface-1 border border-hairline-strong rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-hairline pb-3">
          <div class="flex items-center space-x-2">
            <LogOut class="w-5 h-5 text-amber-400" />
            <h3 class="font-bold text-ink text-sm">Liberar Baia / Cancelar Reserva</h3>
          </div>
          <button class="p-1 text-ink-subtle hover:text-ink" @click="deskToRelease = null">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-3">
          <p class="text-xs text-ink-muted">
            Deseja encerrar e liberar a reserva ativa da estação <strong class="text-ink text-sm">{{ deskToRelease.code }}</strong>?
          </p>
          <p class="text-xs text-ink-subtle leading-relaxed">
            O status da baia passará imediatamente para <strong>DISPONIVEL</strong> e o período restante do agendamento será desocupado, permitindo que outros colaboradores reservem a mesa no mapa 3D.
          </p>

          <div
            v-if="releaseError"
            class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start space-x-2"
          >
            <AlertTriangle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{{ releaseError }}</span>
          </div>
        </div>

        <div class="flex items-center justify-end space-x-2.5 pt-2 border-t border-hairline">
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-surface-2 hover:bg-surface-3 border border-hairline text-ink text-xs font-semibold transition"
            @click="deskToRelease = null"
          >
            Cancelar
          </button>
          <button
            type="button"
            :disabled="isReleasing"
            class="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
            @click="handleReleaseDesk"
          >
            <RefreshCw v-if="isReleasing" class="w-3.5 h-3.5 animate-spin" />
            <span>{{ isReleasing ? 'Liberando...' : 'Sim, Liberar Baia' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
