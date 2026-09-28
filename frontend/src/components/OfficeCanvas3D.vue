<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RefreshCw, RotateCcw, ZoomIn, ZoomOut, Layers } from 'lucide-vue-next';
import { api } from '../services/api';
import type { DeskWithOccupant, Zone } from '../types';
import { createDeskGroup, createOfficeFloor } from '../utils/office3d';

const emit = defineEmits<{
  (e: 'select-desk', desk: DeskWithOccupant): void;
}>();

const containerRef = ref<HTMLDivElement | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const zones = ref<Zone[]>([]);
const selectedZoneId = ref<number | null>(null);
const desks = ref<DeskWithOccupant[]>([]);

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
    const [fetchedZones, fetchedDesks] = await Promise.all([
      api.zones.list(),
      api.bookings.get3dOffice(selectedZoneId.value || undefined),
    ]);
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

  animate();
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
    renderer.dispose();
  }
});
</script>

<template>
  <div class="relative w-full h-[calc(100vh-4rem)] bg-canvas overflow-hidden">
    <!-- WebGL Canvas Container -->
    <div ref="containerRef" class="w-full h-full cursor-grab active:cursor-grabbing" />

    <!-- Top Left Overlay: Zone Selector & Stats -->
    <div class="absolute top-4 left-4 z-10 flex flex-col space-y-2 pointer-events-auto">
      <div class="bg-surface-1/90 backdrop-blur border border-hairline p-3 rounded-lg shadow-xl flex items-center space-x-3">
        <div class="flex items-center space-x-2 text-ink">
          <Layers class="w-4 h-4 text-primary" />
          <span class="text-xs font-semibold uppercase tracking-wider text-ink-subtle">Zona / Andar</span>
        </div>
        <select
          v-model="selectedZoneId"
          class="bg-surface-2 border border-hairline text-ink text-xs rounded-md px-2.5 py-1.5 focus:outline-none focus:border-primary"
        >
          <option :value="null">Todas as Zonas (Geral)</option>
          <option v-for="z in zones" :key="z.id" :value="z.id">
            {{ z.name }} (Andar {{ z.floor }})
          </option>
        </select>
        <button
          class="p-1.5 rounded-md hover:bg-surface-2 text-ink-subtle hover:text-ink transition"
          :class="{ 'animate-spin': isLoading }"
          title="Recarregar baias"
          @click="loadData"
        >
          <RefreshCw class="w-4 h-4" />
        </button>
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
