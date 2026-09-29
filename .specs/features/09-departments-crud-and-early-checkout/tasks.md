# Task List: CRUD de Departamentos e Liberação Antecipada de Reservas

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Create Department model and register relationship with Company and User | `backend/app/models/department.py`, `backend/app/models/user.py`, `backend/app/models/__init__.py` | None | `718112b` (Department model & User department_id created) |
| [x] | TASK-02 | feat | Create Department Pydantic schemas and full CRUD endpoints with referral guards | `backend/app/schemas/department.py`, `backend/app/api/v1/endpoints/departments.py`, `backend/app/api/v1/router.py` | TASK-01 | `718112b` (Schemas & CRUD /departments with referral guard) |
| [x] | TASK-03 | feat | Enhance cancel and early checkout in booking service and expose checkout endpoint | `backend/app/services/booking_service.py`, `backend/app/api/v1/endpoints/bookings.py` | TASK-02 | `718112b` (Early checkout & cancel with end_time truncation) |
| [x] | TASK-04 | test | Add automated pytest tests for Department CRUD and early booking release/cancellation | `backend/tests/test_departments.py`, `backend/tests/test_bookings.py` | TASK-03 | `718112b` (pytest 29 passed in 6.67s) |
| [x] | TASK-05 | feat | Add Department and checkout methods in api.ts and update frontend types | `frontend/src/services/api.ts`, `frontend/src/types/index.ts` | TASK-04 | `718112b` (api.departments & api.bookings.checkout added) |
| [x] | TASK-06 | feat | Add Cancel and Early Checkout buttons and confirmation dialogs in MyBookingsView.vue | `frontend/src/views/MyBookingsView.vue` | TASK-05 | `718112b` (Cancel & Early Checkout buttons with modals) |
| [x] | TASK-07 | feat | Add Departments management tab in AdminUsersView.vue and selector in AuthView.vue | `frontend/src/views/AdminUsersView.vue`, `frontend/src/views/AuthView.vue` | TASK-06 | `718112b` (Corporate departments tab & dynamic selectors) |
| [x] | TASK-08 | review | Run full sensor verification audit (pytest, ruff, npm run build, verify-sdd-integrity) | `backend/tests/`, `frontend/src/` | TASK-07 | `718112b` (npm build 0 err, pytest 29/29, ruff 0 err, SDD OK) |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
