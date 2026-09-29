# Task List: Documentação Central do Projeto & Galeria Visual (README)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build and SDD verification sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Configure Puppeteer automation script to capture high-definition real screenshots of all features | `scripts/capture-screenshots.js`, `frontend/package.json`, `frontend/package-lock.json` | None | Script executed successfully generating 11 PNGs in docs/screenshots/ |
| [x] | TASK-02 | docs | Capture and curate 11 high-definition real screenshots of 3D, 2D, Facilities, QR, Teams and Bookings | `docs/screenshots/` | TASK-01 | 11 PNG screenshots verified in docs/screenshots/ |
| [x] | TASK-03 | docs | Create comprehensive root README.md with badges, showcase gallery, architecture and quickstart guide | `README.md` | TASK-02 | README.md written with full showcase gallery and relative image links |
| [x] | TASK-04 | docs | Add MIT open source license file | `LICENSE` | TASK-03 | Standard MIT License created |
| [x] | TASK-05 | chore | Update .gitignore to exclude temporary browser automation profiles | `.gitignore` | TASK-04 | .edge_profile/ added to .gitignore |
| [x] | TASK-06 | review | Run SDD integrity sensor, spec drift detector, backend tests and frontend production build | `backend/tests/`, `frontend/src/` | TASK-05 | SDD 100% integrity, pytest 34/34 passed, npm run build 0 errors |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
