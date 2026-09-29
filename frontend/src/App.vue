<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Navbar from './components/Navbar.vue';
import OfficeCanvas3D from './components/OfficeCanvas3D.vue';
import BookingModal from './components/BookingModal.vue';
import QRScannerModal from './components/QRScannerModal.vue';
import MyBookingsView from './views/MyBookingsView.vue';
import AdminDesksView from './views/AdminDesksView.vue';
import AdminUsersView from './views/AdminUsersView.vue';
import AuthView from './views/AuthView.vue';
import { useAuth } from './stores/auth';
import type { DeskWithOccupant } from './types';

const auth = useAuth();
const currentTab = ref<'3d-office' | 'my-bookings' | 'admin-desks' | 'admin-users' | 'auth'>('3d-office');
const isBookingModalOpen = ref(false);
const isQrScannerOpen = ref(false);
const selectedDesk = ref<DeskWithOccupant | null>(null);
const officeCanvasRef = ref<{ refresh: () => Promise<void> } | null>(null);

function openBookingModal(desk: DeskWithOccupant) {
  if (!auth.isAuthenticated.value) {
    currentTab.value = 'auth';
    return;
  }
  selectedDesk.value = desk;
  isBookingModalOpen.value = true;
}

function handleLoginSuccess() {
  currentTab.value = '3d-office';
  officeCanvasRef.value?.refresh();
}

function handleBookingCreated() {
  officeCanvasRef.value?.refresh();
  currentTab.value = 'my-bookings';
}

function handleDeskUpdated() {
  officeCanvasRef.value?.refresh();
}

function handleCheckinSuccess() {
  officeCanvasRef.value?.refresh();
}

onMounted(async () => {
  await auth.initAuth();
});
</script>

<template>
  <div class="min-h-screen bg-canvas text-ink flex flex-col font-sans selection:bg-primary/30">
    <Navbar
      :current-tab="currentTab"
      @navigate="(tab) => (currentTab = tab)"
      @open-qr-scanner="isQrScannerOpen = true"
    />

    <main class="flex-1 relative">
      <OfficeCanvas3D
        v-if="currentTab === '3d-office'"
        ref="officeCanvasRef"
        @select-desk="openBookingModal"
      />
      <MyBookingsView
        v-else-if="currentTab === 'my-bookings'"
        @open-qr-scanner="isQrScannerOpen = true"
        @booking-updated="officeCanvasRef?.refresh()"
      />
      <AdminDesksView v-else-if="currentTab === 'admin-desks'" />
      <AdminUsersView v-else-if="currentTab === 'admin-users'" />
      <AuthView
        v-else-if="currentTab === 'auth'"
        @login-success="handleLoginSuccess"
      />
    </main>

    <!-- Global Modals -->
    <BookingModal
      :desk="selectedDesk"
      :is-open="isBookingModalOpen"
      @close="isBookingModalOpen = false"
      @booking-created="handleBookingCreated"
      @desk-updated="handleDeskUpdated"
    />

    <QRScannerModal
      :is-open="isQrScannerOpen"
      @close="isQrScannerOpen = false"
      @checkin-success="handleCheckinSuccess"
    />
  </div>
</template>
