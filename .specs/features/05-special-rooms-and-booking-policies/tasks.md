# Task List: Salas de Reunião Especiais, Restrições de Perfil e Políticas de Tempo de Reserva

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Extend Desk model and schemas with space_type, capacity, required_role and max_duration | `backend/app/models/desk.py`, `backend/app/schemas/desk.py` | None | Models and schemas validated |
| [x] | TASK-02 | feat | Implement role restriction and max duration validations in booking service and endpoint | `backend/app/services/booking_service.py`, `backend/app/api/v1/endpoints/bookings.py` | TASK-01 | Validated via service unit logic |
| [x] | TASK-03 | feat | Seed demo meeting rooms with policies and add automated test coverage | `backend/app/db/init_db.py`, `backend/tests/test_bookings.py` | TASK-02 | pytest: 18 passed in 3.19s |
| [x] | TASK-04 | feat | Update BookingModal with policy badges and AdminDesksView with room builder controls | `frontend/src/types/index.ts`, `frontend/src/components/BookingModal.vue`, `frontend/src/views/AdminDesksView.vue` | TASK-03 | npm run build: built in 1.41s |
| [x] | TASK-05 | review | Run full sensor verification audit (pytest, ruff, npm run build, sdd sensor) | `backend/tests/`, `frontend/src/` | TASK-04 | 18 passed, ruff clean, build 0 err, sdd 100% |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
