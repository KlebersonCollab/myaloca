# Task List: Core Booking, Desks & QR-Code Check-in System

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Decoupled Test Setup**: Test definition / scaffolding tasks (`Type: test`) MUST precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [ ] | TASK-01 | test | Scaffold test fixtures, async db engine, and test client | `backend/tests/conftest.py` | None | |
| [ ] | TASK-02 | feat | Configure Python project with uv, core settings and FastAPI app | `backend/pyproject.toml`, `backend/app/main.py`, `backend/app/core/config.py` | TASK-01 | |
| [ ] | TASK-03 | feat | Setup SQLAlchemy 2.0 async engine and declarative base | `backend/app/db/session.py`, `backend/app/db/base.py` | TASK-02 | |
| [ ] | TASK-04 | test | Write test suite for JWT authentication and user profile | `backend/tests/test_auth.py` | TASK-03 | |
| [ ] | TASK-05 | feat | Implement User model, security utilities, and auth routes | `backend/app/models/user.py`, `backend/app/schemas/user.py`, `backend/app/api/v1/endpoints/auth.py` | TASK-04 | |
| [ ] | TASK-06 | test | Write test suite for Zones, 3D Desks, and QR Code generation | `backend/tests/test_desks.py` | TASK-05 | |
| [ ] | TASK-07 | feat | Implement Zone, Desk models, schemas, and QR engine | `backend/app/models/desk.py`, `backend/app/schemas/desk.py`, `backend/app/services/desk_service.py` | TASK-06 | |
| [ ] | TASK-08 | feat | Implement Desk and Zone REST endpoints and router integration | `backend/app/api/v1/endpoints/zones.py`, `backend/app/api/v1/endpoints/desks.py`, `backend/app/api/v1/router.py` | TASK-07 | |
| [ ] | TASK-09 | test | Write test suite for booking overlaps, QR check-in, and auto-release | `backend/tests/test_bookings.py` | TASK-08 | |
| [ ] | TASK-10 | feat | Implement Booking model and Pydantic schemas | `backend/app/models/booking.py`, `backend/app/schemas/booking.py` | TASK-09 | |
| [ ] | TASK-11 | feat | Implement BookingService and booking/check-in endpoints | `backend/app/services/booking_service.py`, `backend/app/api/v1/endpoints/bookings.py` | TASK-10 | |
| [ ] | TASK-12 | feat | Implement async background scheduler for no-show auto-release | `backend/app/core/scheduler.py`, `backend/app/db/init_db.py` | TASK-11 | |
| [ ] | TASK-13 | review | Run full sensor audit (ruff, pytest, verify-sdd-integrity) | `backend/tests/`, `backend/app/` | TASK-12 | |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
