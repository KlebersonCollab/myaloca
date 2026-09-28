# Task List: Frontend Vue 3 + 3D Office Canvas & Hot-Desking Experience

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Decoupled Setup**: Tooling and core stores precede UI view implementation.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [ ] | TASK-01 | feat | Initialize Vite Vue 3 TypeScript project with Tailwind CSS | `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tailwind.config.js` | None | |
| [ ] | TASK-02 | feat | Configure API client, TypeScript domain types, and auth store | `frontend/src/services/api.ts`, `frontend/src/types/index.ts`, `frontend/src/stores/auth.ts` | TASK-01 | |
| [ ] | TASK-03 | feat | Implement layout, Navbar, and Linear Dark styling | `frontend/src/components/Navbar.vue`, `frontend/src/App.vue`, `frontend/src/style.css` | TASK-02 | |
| [ ] | TASK-04 | feat | Implement 3D Office Canvas with Three.js and OrbitControls | `frontend/src/components/OfficeCanvas3D.vue`, `frontend/src/components/DeskModal.vue` | TASK-03 | |
| [ ] | TASK-05 | feat | Implement 3D desk geometries, status materials, and avatar badges | `frontend/src/utils/office3d.ts`, `frontend/src/components/DeskBadge.vue` | TASK-04 | |
| [ ] | TASK-06 | feat | Implement Booking drawer modal and My Bookings view | `frontend/src/components/BookingModal.vue`, `frontend/src/views/MyBookingsView.vue` | TASK-05 | |
| [ ] | TASK-07 | feat | Implement QR Code camera scanner and Manager Desks panel | `frontend/src/components/QRScannerModal.vue`, `frontend/src/views/AdminDesksView.vue` | TASK-06 | |
| [ ] | TASK-08 | review | Run frontend build sensor (npm run build) and SDD audit | `frontend/dist/`, `frontend/src/` | TASK-07 | |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
