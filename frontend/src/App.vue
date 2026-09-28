<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Navbar from './components/Navbar.vue';
import OfficeCanvas3D from './components/OfficeCanvas3D.vue';
import BookingModal from './components/BookingModal.vue';
import QRScannerModal from './components/QRScannerModal.vue';
import MyBookingsView from './views/MyBookingsView.vue';
import AdminDesksView from './views/AdminDesksView.vue';
import { useAuth } from './stores/auth';
import type { DeskWithOccupant } from './types';

const auth = useAuth();
const currentTab = ref<'3d-office' | 'my-bookings' | 'admin-desks'>('3d-office');
const isBookingModalOpen = ref(false);
const isQrScannerOpen = ref(false);
const selectedDesk = ref<DeskWithOccupant | null>(null);
const officeKey = ref(0);

function openBookingModal(desk: DeskWithOccupant) {
  selectedDesk.value = desk;
  isBookingModalOpen.value = true;
}

function handleBookingCreated() {
  officeKey.value++; // Refresh 3D scene
  currentTab.value = 'my-bookings';
}

function handleCheckinSuccess() {
  officeKey.value++; // Refresh 3D scene
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
        :key="officeKey"
        @select-desk="openBookingModal"
      />
      <MyBookingsView
        v-else-if="currentTab === 'my-bookings'"
        @open-qr-scanner="isQrScannerOpen = true"
      />
      <AdminDesksView v-else-if="currentTab === 'admin-desks'" />
    </main>

    <!-- Global Modals -->
    <BookingModal
      :desk="selectedDesk"
      :is-open="isBookingModalOpen"
      @close="isBookingModalOpen = false"
      @booking-created="handleBookingCreated"
    />

    <QRScannerModal
      :is-open="isQrScannerOpen"
      @close="isQrScannerOpen = false"
      @checkin-success="handleCheckinSuccess"
    />
  </div>
</template>
