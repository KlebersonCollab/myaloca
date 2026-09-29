# Task List: Planta Dinâmica, Edição de Equipamentos e Drag & Drop de Baias

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Add grid_cols, grid_rows to Zone and monitors_count, extra_equipment to Desk model, schemas and DeskService | `backend/app/models/desk.py`, `backend/app/schemas/desk.py`, `backend/app/services/desk_service.py` | None | Models and schemas extended with bidirectional has_monitor sync |
| [x] | TASK-02 | test | Add automated pytest tests for Zone grid dimensions, Desk equipment update and repositioning | `backend/tests/test_desks.py` | TASK-01 | 33 passed in 7.45s (`uv run pytest`) |
| [x] | TASK-03 | feat | Update init_db.py seed data to create Company, Building, Departments, dynamic grids and rich equipment | `backend/app/db/init_db.py` | TASK-02 | Seed verified; Company, Building, 4 Depts, 3 Floors (6x4, 8x4, 6x3) populated |
| [x] | TASK-04 | feat | Update types and Three.js office3d.ts for dynamic monitors_count (0, 1, 2) | `frontend/src/types/index.ts`, `frontend/src/utils/office3d.ts` | TASK-03 | Three.js meshes rendered for 0, 1 centered, 2 stereo monitors and docking station |
| [x] | TASK-05 | feat | Implement dynamic grid, equipment editor and 2D Drag & Drop in AdminDesksView.vue | `frontend/src/views/AdminDesksView.vue` | TASK-04 | Dynamic CSS grid toolbar, HTML5 drag & drop, equipment modal |
| [x] | TASK-06 | feat | Implement 3D Drag & Drop mode in OfficeCanvas3D.vue and in-map desk editing in BookingModal.vue | `frontend/src/components/OfficeCanvas3D.vue`, `frontend/src/components/BookingModal.vue` | TASK-05 | Move mode toggle, Three.js raycasting ground-plane drag with 0.6m snap and in-map desk editor |
| [x] | TASK-07 | review | Run full sensor verification audit (pytest, ruff, npm run build, verify-sdd-integrity) | `backend/tests/`, `frontend/src/` | TASK-06 | All 4 sensors passed: pytest 33/33, ruff 0 errors, npm build 0 errors, SDD integrity 100% |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
