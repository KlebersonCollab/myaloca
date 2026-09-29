# Task List: Edição de Perfil, Cargos e Gestão de Usuários

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Create Admin user schemas (AdminUserCreate, AdminUserUpdate) and update UserUpdate | `backend/app/schemas/user.py` | None | `718112b` (Pydantic admin schemas created) |
| [x] | TASK-02 | feat | Implement Users CRUD endpoints in users.py and register in router.py | `backend/app/api/v1/endpoints/users.py`, `backend/app/api/v1/router.py` | TASK-01 | `718112b` (Full Users CRUD endpoints implemented) |
| [x] | TASK-03 | test | Add automated test coverage for Users CRUD, role promotions and self-deletion guard | `backend/tests/test_users.py` | TASK-02 | `718112b` (pytest 26 passed in 5.56s) |
| [x] | TASK-04 | feat | Add users CRUD and updateMe API methods and auth store update action | `frontend/src/services/api.ts`, `frontend/src/stores/auth.ts` | TASK-03 | `718112b` (API methods & updateProfile store action) |
| [x] | TASK-05 | feat | Build interactive profile editor in AuthView.vue for self-service profile & cargo updates | `frontend/src/views/AuthView.vue` | TASK-04 | `718112b` (Interactive profile & cargo editor) |
| [x] | TASK-06 | feat | Create AdminUsersView.vue for team & roles management and add navbar link | `frontend/src/views/AdminUsersView.vue`, `frontend/src/components/Navbar.vue`, `frontend/src/App.vue` | TASK-05 | `718112b` (Team & roles hub with navbar integration) |
| [x] | TASK-07 | review | Run full sensor verification audit (pytest, ruff, npm run build, sdd sensor) | `backend/tests/`, `frontend/src/` | TASK-06 | `718112b` (npm build 0 err, pytest 26/26, ruff OK, SDD OK) |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
