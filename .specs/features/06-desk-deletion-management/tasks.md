# Task List: Remoção Segura de Baias e Governança de Dependências

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Implement delete_desk in service with active booking guard and DELETE endpoint | `backend/app/services/desk_service.py`, `backend/app/api/v1/endpoints/desks.py` | None | Service & DELETE endpoint validated |
| [x] | TASK-02 | test | Add automated test coverage for desk deletion, active booking error and role check | `backend/tests/test_desks.py` | TASK-01 | pytest: 21 passed in 5.26s |
| [x] | TASK-03 | feat | Add delete method to frontend API client | `frontend/src/services/api.ts` | TASK-02 | api.desks.delete compiled |
| [x] | TASK-04 | feat | Add delete action and confirmation dialog to AdminDesksView | `frontend/src/views/AdminDesksView.vue` | TASK-03 | npm run build: built in 1.87s |
| [x] | TASK-05 | review | Run full sensor verification audit (pytest, ruff, npm run build, sdd sensor) | `backend/tests/`, `frontend/src/` | TASK-04 | 21 passed, ruff clean, build 0 err, sdd 100% |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
