# Task List: Suporte a Prédios Multi-Andares e Construtor Visual de Baias Sem Coordenadas Manuais

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Add floor query filters and batch desk creation endpoint in backend | `backend/app/api/v1/endpoints/desks.py`, `backend/app/api/v1/endpoints/zones.py`, `backend/app/api/v1/endpoints/bookings.py` | None | POST /desks/batch, GET ?floor=X filters added and validated |
| [x] | TASK-02 | feat | Seed realistic multi-floor building data and add test coverage | `backend/app/db/init_db.py`, `backend/tests/test_desks.py` | TASK-01 | 16/16 pytest passing, Floor 1, 2, 3 seeded in SQLite |
| [x] | TASK-03 | feat | Implement multi-floor building switcher tabs in 3D Office Canvas | `frontend/src/services/api.ts`, `frontend/src/components/OfficeCanvas3D.vue` | TASK-02 | Building tabs (1º, 2º, 3º, Todos) + zone filter inside floor |
| [x] | TASK-04 | feat | Implement visual desk builder, row assistant and new floor modal | `frontend/src/views/AdminDesksView.vue` | TASK-03 | Row builder assistant (batch 2..6), 2D floorplan grid click-to-place |
| [x] | TASK-05 | review | Run full sensor verification audit (pytest, ruff, npm run build, sdd sensor) | `backend/tests/`, `frontend/src/` | TASK-04 | npm run build 0 errors, pytest 16 passed, ruff 0 errors, SDD 100% |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
