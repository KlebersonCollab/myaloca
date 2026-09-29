<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RefreshCw, RotateCcw, ZoomIn, ZoomOut, Layers, Building2 } from 'lucide-vue-next';
import { api } from '../services/api';
import type { Building, DeskWithOccupant, Zone } from '../types';
import { createDeskGroup, createOfficeFloor } from '../utils/office3d';

const emit = defineEmits<{
  (e: 'select-desk', desk: DeskWithOccupant): void;
}>();

const containerRef = ref<HTMLDivElement | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const buildings = ref<Building[]>([]);
const selectedBuildingId = ref<number | null>(null);
const zones = ref<Zone[]>([]);
const selectedFloor = ref<number | null>(1);
const selectedZoneId = ref<number | null>(null);
const desks = ref<DeskWithOccupant[]>([]);

const availableFloors = computed(() => {
  const floors = new Set<number>();
  zones.value.forEach((z) => {
    if (selectedBuildingId.value !== null && z.building_id !== selectedBuildingId.value) {
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
    if (selectedBuildingId.value !== null && z.building_id !== selectedBuildingId.value) {
      return false;
    }
    if (selectedFloor.value !== null && z.floor !== selectedFloor.value) {
      return false;
    }
    return true;
  });
});

let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;
let animationFrameId: number;
let deskObjectsGroup: THREE.Group;
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

async function loadData() {
  isLoading.value = true;
  error.value = null;
  try {
    const [fetchedBuildings, fetchedZones, fetchedDesks] = await Promise.all([
      api.buildings.list(),
      api.zones.list(
        selectedFloor.value !== null ? selectedFloor.value : undefined,
        selectedBuildingId.value !== null ? selectedBuildingId.value : undefined
      ),
      api.bookings.get3dOffice(
        selectedZoneId.value || undefined,
        selectedFloor.value !== null ? selectedFloor.value : undefined
      ),
    ]);
    buildings.value = fetchedBuildings;
    zones.value = fetchedZones;
    desks.value = fetchedDesks;
    renderDesksInScene();
  } catch (err: any) {
    error.value = err.message || 'Falha ao carregar mapa 3D';
  } finally {
    isLoading.value = false;
  }
}

function initScene() {
  if (!containerRef.value) return;

  const width = containerRef.value.clientWidth;
  const height = containerRef.value.clientHeight || 600;

  // 1. Scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x010102);
  scene.fog = new THREE.FogExp2(0x010102, 0.035);

  // 2. Camera
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
  camera.position.set(0, 12, 14);

  // 3. Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  containerRef.value.appendChild(renderer.domElement);

  // 4. Controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.maxPolarAngle = Math.PI / 2.1; // Don't allow camera under floor
  controls.minDistance = 3;
  controls.maxDistance = 35;
  controls.target.set(0, 0, 0);

  // 5. Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);

  const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
  mainLight.position.set(10, 20, 10);
  mainLight.castShadow = true;
  mainLight.shadow.mapSize.width = 2048;
  mainLight.shadow.mapSize.height = 2048;
  mainLight.shadow.bias = -0.0001;
  scene.add(mainLight);

  const fillLight = new THREE.DirectionalLight(0x5e6ad2, 0.4);
  fillLight.position.set(-10, 15, -10);
  scene.add(fillLight);

  // 6. Floor & Grid
  const floor = createOfficeFloor(36, 36);
  scene.add(floor);

  // 7. Desks Group
  deskObjectsGroup = new THREE.Group();
  scene.add(deskObjectsGroup);

  // 8. Event Listeners
  window.addEventListener('resize', onWindowResize);
  renderer.domElement.addEventListener('click', onCanvasClick);
  renderer.domElement.addEventListener('mousemove', onCanvasMouseMove);
  renderer.domElement.addEventListener('mouseleave', onCanvasMouseLeave);

  animate();
}

const hoveredDesk = ref<DeskWithOccupant | null>(null);
const tooltipPos = ref<{ x: number; y: number }>({ x: 0, y: 0 });

function onCanvasMouseMove(event: MouseEvent) {
  if (!containerRef.value || !renderer || !camera || !deskObjectsGroup) return;
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(deskObjectsGroup.children, true);

  if (intersects.length > 0) {
    let topParent = intersects[0].object;
    while (topParent.parent && topParent.parent !== deskObjectsGroup) {
      topParent = topParent.parent;
    }
    const deskData = topParent.userData?.desk as DeskWithOccupant | undefined;
    if (deskData) {
      hoveredDesk.value = deskData;
      tooltipPos.value = {
        x: Math.min(event.clientX - rect.left + 15, rect.width - 280),
        y: Math.min(event.clientY - rect.top + 15, rect.height - 180),
      };
      renderer.domElement.style.cursor = 'pointer';
      return;
    }
  }

  hoveredDesk.value = null;
  renderer.domElement.style.cursor = 'default';
}

function onCanvasMouseLeave() {
  hoveredDesk.value = null;
}

function renderDesksInScene() {
  if (!deskObjectsGroup) return;

  // Clear existing desk meshes
  while (deskObjectsGroup.children.length > 0) {
    const obj = deskObjectsGroup.children[0];
    deskObjectsGroup.remove(obj);
  }

  // Populate desks
  desks.value.forEach((desk) => {
    const deskGroup = createDeskGroup(desk);
    deskObjectsGroup.add(deskGroup);
  });
}

function animate() {
  animationFrameId = requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

function onWindowResize() {
  if (!containerRef.value || !renderer || !camera) return;
  const width = containerRef.value.clientWidth;
  const height = containerRef.value.clientHeight || 600;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

function onCanvasClick(event: MouseEvent) {
  if (!containerRef.value) return;
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(deskObjectsGroup.children, true);

  if (intersects.length > 0) {
    let topParent = intersects[0].object;
    while (topParent.parent && topParent.parent !== deskObjectsGroup) {
      topParent = topParent.parent;
    }
    const deskData = topParent.userData?.desk as DeskWithOccupant | undefined;
    if (deskData) {
      emit('select-desk', deskData);
    }
  }
}

function resetCamera() {
  camera.position.set(0, 12, 14);
  controls.target.set(0, 0, 0);
  controls.update();
}

function zoomCamera(direction: 'in' | 'out') {
  const factor = direction === 'in' ? 0.8 : 1.25;
  camera.position.multiplyScalar(factor);
  controls.update();
}

watch(selectedBuildingId, () => {
  selectedZoneId.value = null;
  loadData();
});

watch(selectedFloor, () => {
  selectedZoneId.value = null;
  loadData();
});

watch(selectedZoneId, () => {
  loadData();
});

onMounted(async () => {
  initScene();
  await loadData();
});

onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrameId);
  window.removeEventListener('resize', onWindowResize);
  if (renderer && renderer.domElement) {
    renderer.domElement.removeEventListener('click', onCanvasClick);
    renderer.domElement.removeEventListener('mousemove', onCanvasMouseMove);
    renderer.domElement.removeEventListener('mouseleave', onCanvasMouseLeave);
    renderer.dispose();
  }
});
</script>

<template>
  <div class="relative w-full h-[calc(100vh-4rem)] bg-canvas overflow-hidden">
    <!-- WebGL Canvas Container -->
    <div ref="containerRef" class="w-full h-full cursor-grab active:cursor-grabbing" />

    <!-- Interactive Floating Desk Tooltip -->
    <div
      v-if="hoveredDesk"
      class="absolute z-30 pointer-events-none transition-all duration-75"
      :style="{ left: `${tooltipPos.x}px`, top: `${tooltipPos.y}px` }"
    >
      <div class="bg-surface-1/95 border border-hairline/80 backdrop-blur-md rounded-xl p-3 shadow-2xl w-64 text-xs space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-1.5">
            <span class="w-2 h-2 rounded-full"
              :class="{
                'bg-emerald-400': hoveredDesk.status === 'DISPONIVEL',
                'bg-primary': hoveredDesk.status === 'OCUPADA',
                'bg-amber-400': hoveredDesk.status === 'RESERVADA',
                'bg-zinc-500': hoveredDesk.status === 'MANUTENCAO',
              }"
            />
            <span class="font-bold text-sm text-ink tracking-tight">
              {{ hoveredDesk.space_type === 'SALA_REUNIAO' ? 'Sala ' : (hoveredDesk.space_type === 'CABINE_FOCUS' ? 'Cabine ' : 'Baia ') }}{{ hoveredDesk.code }}
            </span>
          </div>
          <span
            class="px-2 py-0.5 rounded-full font-semibold text-[10px] uppercase tracking-wider"
            :class="{
              'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30': hoveredDesk.status === 'DISPONIVEL',
              'bg-primary/20 text-primary border border-primary/30': hoveredDesk.status === 'OCUPADA',
              'bg-amber-500/20 text-amber-400 border border-amber-500/30': hoveredDesk.status === 'RESERVADA',
              'bg-surface-3 text-ink-subtle': hoveredDesk.status === 'MANUTENCAO',
            }"
          >
            {{ hoveredDesk.status }}
          </span>
        </div>

        <!-- Occupant Card if reserved or occupied -->
        <div
          v-if="hoveredDesk.occupant_name"
          class="flex items-center space-x-2.5 bg-surface-2/80 p-2 rounded-lg border border-hairline/60"
        >
          <img
            v-if="hoveredDesk.occupant_photo || hoveredDesk.occupant_avatar"
            :src="(hoveredDesk.occupant_photo || hoveredDesk.occupant_avatar) as string"
            class="w-9 h-9 rounded-full border border-hairline bg-surface-3 object-cover shrink-0"
            alt="Avatar"
          />
          <div v-else class="w-9 h-9 rounded-full bg-primary/20 text-primary font-bold flex items-center justify-center shrink-0">
            {{ hoveredDesk.occupant_name.charAt(0) }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="font-semibold text-ink truncate text-xs">{{ hoveredDesk.occupant_name }}</p>
            <p class="text-[10px] text-ink-subtle flex items-center space-x-1">
              <span>{{ hoveredDesk.status === 'OCUPADA' ? 'Check-in físico ativo' : 'Reserva confirmada' }}</span>
            </p>
          </div>
        </div>

        <div v-else class="text-ink-subtle text-[11px] py-0.5 flex flex-col space-y-0.5">
          <span>{{ hoveredDesk.space_type === 'SALA_REUNIAO' ? 'Sala livre para agendamento.' : (hoveredDesk.space_type === 'CABINE_FOCUS' ? 'Cabine focus livre.' : 'Baia livre para agendamento presencial.') }}</span>
          <span v-if="hoveredDesk.max_duration_minutes" class="text-amber-400 font-medium">
            ⏱️ Máx {{ hoveredDesk.max_duration_minutes >= 60 ? `${hoveredDesk.max_duration_minutes / 60}h` : `${hoveredDesk.max_duration_minutes}m` }} por reserva
          </span>
          <span v-if="hoveredDesk.required_role === 'gestor'" class="text-purple-400 font-medium">
            🔒 Exclusivo para Gestores
          </span>
        </div>

        <!-- Specs & Facilities -->
        <div class="flex items-center space-x-2 pt-1.5 border-t border-hairline/60 text-[10px] text-ink-muted">
          <span v-if="hoveredDesk.has_monitor" class="flex items-center space-x-1">
            <span>🖥️ Monitor duplo</span>
          </span>
          <span v-if="hoveredDesk.has_docking_station" class="flex items-center space-x-1">
            <span>🔌 Docking USB-C</span>
          </span>
          <span v-if="hoveredDesk.is_standing_desk" class="flex items-center space-x-1">
            <span>⬆️ Altura regulável</span>
          </span>
        </div>

        <div class="text-[10px] text-primary/90 font-medium pt-0.5">
          👉 Clique para {{ hoveredDesk.status === 'DISPONIVEL' ? 'reservar' : 'ver detalhes' }}
        </div>
      </div>
    </div>

    <!-- Top Left Overlay: Multi-Floor Building Selector & Stats -->
    <div class="absolute top-4 left-4 z-10 flex flex-col space-y-2 pointer-events-auto">
      <div class="bg-surface-1/95 backdrop-blur-md border border-hairline p-3 rounded-xl shadow-2xl flex flex-col space-y-2.5 min-w-[280px]">
        <!-- Floor Tabs Header -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2 text-ink">
            <Building2 class="w-4 h-4 text-primary" />
            <span class="text-xs font-bold uppercase tracking-wider text-ink">Edifício • Andares</span>
          </div>
          <button
            class="p-1 rounded-md hover:bg-surface-2 text-ink-subtle hover:text-ink transition"
            :class="{ 'animate-spin': isLoading }"
            title="Recarregar baias"
            @click="loadData"
          >
            <RefreshCw class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Building Selector Dropdown (if multiple buildings) -->
        <div v-if="buildings.length > 0" class="flex items-center space-x-2">
          <select
            v-model="selectedBuildingId"
            class="bg-surface-2 border border-hairline text-ink text-xs rounded-md px-2 py-1.5 focus:outline-none focus:border-primary flex-1"
          >
            <option :value="null">Todos os Edifícios</option>
            <option v-for="b in buildings" :key="b.id" :value="b.id">
              🏢 {{ b.name }} ({{ b.code }})
            </option>
          </select>
        </div>

        <!-- Floor Switcher Tabs -->
        <div class="flex items-center space-x-1 bg-surface-2/80 p-1 rounded-lg border border-hairline overflow-x-auto">
          <button
            v-for="fl in availableFloors"
            :key="fl"
            type="button"
            class="px-2.5 py-1 text-xs font-semibold rounded-md transition whitespace-nowrap"
            :class="selectedFloor === fl ? 'bg-primary text-white shadow-sm' : 'text-ink-subtle hover:text-ink hover:bg-surface-3'"
            @click="selectedFloor = fl"
          >
            {{ fl }}º Andar
          </button>
          <button
            type="button"
            class="px-2.5 py-1 text-xs font-semibold rounded-md transition whitespace-nowrap"
            :class="selectedFloor === null ? 'bg-primary text-white shadow-sm' : 'text-ink-subtle hover:text-ink hover:bg-surface-3'"
            @click="selectedFloor = null"
          >
            Todos
          </button>
        </div>

        <!-- Zone Selector inside Current Floor -->
        <div class="flex items-center space-x-2 pt-1 border-t border-hairline/60">
          <Layers class="w-3.5 h-3.5 text-primary shrink-0" />
          <select
            v-model="selectedZoneId"
            class="bg-surface-2 border border-hairline text-ink text-xs rounded-md px-2 py-1.5 focus:outline-none focus:border-primary flex-1"
          >
            <option :value="null">Todas as Zonas {{ selectedFloor ? `do ${selectedFloor}º Andar` : '' }}</option>
            <option v-for="z in filteredZones" :key="z.id" :value="z.id">
              {{ z.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Quick Metrics Pill -->
      <div class="bg-surface-1/80 backdrop-blur border border-hairline px-3 py-1.5 rounded-md flex items-center space-x-4 text-xs">
        <span class="text-ink-subtle">Total: <strong class="text-ink">{{ desks.length }}</strong></span>
        <span class="text-emerald-400">Livres: <strong>{{ desks.filter(d => d.status === 'DISPONIVEL').length }}</strong></span>
        <span class="text-purple-400">Ocupadas: <strong>{{ desks.filter(d => d.status === 'OCUPADA').length }}</strong></span>
        <span class="text-amber-400">Reservadas: <strong>{{ desks.filter(d => d.status === 'RESERVADA').length }}</strong></span>
      </div>
    </div>

    <!-- Bottom Left Legend -->
    <div class="absolute bottom-4 left-4 z-10 pointer-events-auto">
      <div class="bg-surface-1/90 backdrop-blur border border-hairline p-3 rounded-lg shadow-xl flex items-center space-x-4 text-xs">
        <div class="flex items-center space-x-1.5">
          <span class="w-3 h-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50" />
          <span class="text-ink-muted">Disponível</span>
        </div>
        <div class="flex items-center space-x-1.5">
          <span class="w-3 h-3 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50" />
          <span class="text-ink-muted">Reservada</span>
        </div>
        <div class="flex items-center space-x-1.5">
          <span class="w-3 h-3 rounded-full bg-primary shadow-sm shadow-primary/50" />
          <span class="text-ink-muted">Ocupada</span>
        </div>
      </div>
    </div>

    <!-- Bottom Right Controls: Zoom & Reset -->
    <div class="absolute bottom-4 right-4 z-10 flex flex-col space-y-1.5 pointer-events-auto">
      <button
        class="w-8 h-8 rounded-lg bg-surface-1/90 backdrop-blur border border-hairline hover:bg-surface-2 text-ink flex items-center justify-center shadow-lg transition active:scale-95"
        title="Aproximar Zoom"
        @click="zoomCamera('in')"
      >
        <ZoomIn class="w-4 h-4" />
      </button>
      <button
        class="w-8 h-8 rounded-lg bg-surface-1/90 backdrop-blur border border-hairline hover:bg-surface-2 text-ink flex items-center justify-center shadow-lg transition active:scale-95"
        title="Afastar Zoom"
        @click="zoomCamera('out')"
      >
        <ZoomOut class="w-4 h-4" />
      </button>
      <button
        class="w-8 h-8 rounded-lg bg-surface-1/90 backdrop-blur border border-hairline hover:bg-surface-2 text-ink flex items-center justify-center shadow-lg transition active:scale-95"
        title="Resetar Câmera"
        @click="resetCamera"
      >
        <RotateCcw class="w-4 h-4" />
      </button>
    </div>

    <!-- Hint Floating Center -->
    <div class="absolute top-4 right-4 z-10 pointer-events-none">
      <span class="text-[11px] text-ink-subtle bg-surface-1/80 border border-hairline px-2.5 py-1 rounded-full backdrop-blur">
        💡 Arraste para girar • Scroll para zoom • Clique numa baia para reservar
      </span>
    </div>
  </div>
</template>
