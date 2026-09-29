# Task List: Cancelamento Administrativo e Liberação de Baias

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Implement desk release logic in desk_service.py and add POST /desks/{id}/release endpoint | `backend/app/services/desk_service.py`, `backend/app/api/v1/endpoints/desks.py` | None | Commit 718112b: release_desk added |
| [x] | TASK-02 | test | Add automated pytest tests for desk release and RBAC security guards | `backend/tests/test_desks.py` | TASK-01 | Commit 718112b: pytest 31/31 passed |
| [x] | TASK-03 | feat | Add desk release method in api.ts | `frontend/src/services/api.ts` | TASK-02 | Commit 718112b: api.desks.release implemented |
| [x] | TASK-04 | feat | Add Liberar Baia button and confirmation modal in AdminDesksView.vue | `frontend/src/views/AdminDesksView.vue` | TASK-03 | Commit 718112b: Action button and dialog integrated |
| [x] | TASK-05 | feat | Add admin release action button for occupied desks in BookingModal.vue | `frontend/src/components/BookingModal.vue` | TASK-04 | Commit 718112b: Booking modal release for admin/gestor |
| [x] | TASK-06 | review | Run full sensor verification audit (pytest, ruff, npm run build, verify-sdd-integrity) | `backend/tests/`, `frontend/src/` | TASK-05 | All sensors passed: pytest 31/31, ruff 0 err, build 0 err, SDD 100% |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
