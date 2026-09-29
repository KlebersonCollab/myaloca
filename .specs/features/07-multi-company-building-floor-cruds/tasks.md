# Task List: Hierarquia Corporativa Completa (Empresas, Prédios, Andares e Baias com CRUDs Completos)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Create Company and Building models, update Zone with building_id, and add schemas | `backend/app/models/building.py`, `backend/app/models/desk.py`, `backend/app/schemas/building.py` | None | `718112b` (Models & Pydantic schemas created) |
| [x] | TASK-02 | feat | Implement Building and Zone CRUD endpoints and desk PUT update route | `backend/app/services/building_service.py`, `backend/app/api/v1/endpoints/buildings.py`, `backend/app/api/v1/endpoints/zones.py` | TASK-01 | `718112b` (Full CRUD routes in router.py) |
| [x] | TASK-03 | test | Add automated test coverage for Building, Zone CRUDs and Desk updates | `backend/tests/test_buildings.py` | TASK-02 | `718112b` (pytest 24 passed in 11.27s) |
| [x] | TASK-04 | feat | Update frontend types and API client with full building, zone and desk CRUD methods | `frontend/src/types/index.ts`, `frontend/src/services/api.ts` | TASK-03 | `718112b` (TypeScript build passed) |
| [x] | TASK-05 | feat | Build Unified Facilities Hub in AdminDesksView with Building, Floor, and Desk CRUD tabs | `frontend/src/views/AdminDesksView.vue` | TASK-04 | `718112b` (npm run build 0 errors) |
| [x] | TASK-06 | review | Run full sensor verification audit (pytest, ruff, npm run build, sdd sensor) | `backend/tests/`, `frontend/src/` | TASK-05 | `718112b` (ruff 0 errors, pytest 24/24, SDD OK) |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
