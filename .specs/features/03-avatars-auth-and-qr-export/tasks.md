# Task List: 3D Avatars, Occupant Visibility, Dedicated Auth UI & QR Code Export

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Seed demo bookings with avatars and adjust 3D layout query | `backend/app/db/init_db.py`, `backend/app/services/booking_service.py` | None | pytest 15 passed, DB seeded with Lucas Dev & Mariana Silva |
| [x] | TASK-02 | feat | Implement 3D avatar billboard cards and occupant hover tooltips | `frontend/src/utils/office3d.ts`, `frontend/src/components/OfficeCanvas3D.vue` | TASK-01 | Seated humanoid mesh + billboard card + hover tooltip |
| [x] | TASK-03 | feat | Implement authenticated QR Code Blob download and print preview modal | `frontend/src/services/api.ts`, `frontend/src/views/AdminDesksView.vue` | TASK-02 | Blob download helper + modal printable sticker preview |
| [x] | TASK-04 | feat | Implement dedicated Login, Register with Avatar Picker, and Profile view | `frontend/src/views/AuthView.vue`, `frontend/src/components/Navbar.vue`, `frontend/src/App.vue` | TASK-03 | AuthView with Login, Register (DiceBear picker), Profile |
| [x] | TASK-05 | review | Run full sensor audit (pytest, ruff, npm run build, sdd sensor) | `backend/tests/`, `frontend/src/` | TASK-04 | npm run build (0 errors), pytest (15 passed), ruff (0 errors), sdd 100% |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
