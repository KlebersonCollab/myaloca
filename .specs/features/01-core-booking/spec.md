# Specification: Core Booking, Desks & QR-Code Check-in System

## 1. User Stories
- **US-1**: As a `Gestor`, I want to register desks with 3D coordinates and generate an immutable QR code, so that employees can locate and physically check into the desk.
- **US-2**: As an `Employee`, I want to reserve an available desk for a specific time range in advance, so that I have a guaranteed workspace on my in-office day.
- **US-3**: As an `Employee`, I want to scan the desk's physical QR code to check in, so that my reservation remains active and my avatar appears on the desk.
- **US-4**: As a `System Administrator`, I want unconfirmed reservations to automatically expire after the 30-minute grace period, so that unoccupied desks become immediately available for other employees.

## 2. Business Rules & Invariants
- **BR-1 (Booking Window)**: Bookings must have `start_time < end_time` and `start_time >= now()`.
- **BR-2 (Collision Prevention)**: A desk cannot have overlapping active bookings (`PENDENTE_CHECKIN` or `CHECKED_IN`) for any given time interval.
- **BR-3 (Check-in Grace Period)**: Check-in is valid only from `start_time - 15 minutes` up to `start_time + 30 minutes`.
- **BR-4 (Auto-Release / No-Show)**: Any reservation in `PENDENTE_CHECKIN` status where current UTC time exceeds `start_time + 30 minutes` must be automatically transitioned to `EXPIRADA_NO_SHOW` and the desk freed.
- **BR-5 (QR-Code Immutability)**: Each desk has a permanent cryptographic token `qr_code_hash`. Check-in requires passing this exact hash.
- **BR-6 (Role Permissions)**: Only users with role `admin` or `manager` can create/update zones and desks or download QR codes.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Create Desk with 3D Coordinates and QR Token**
  - **Given** an authenticated user with role `admin`
  - **When** POST `/api/v1/desks` is called with code `BAIA-101`, zone_id, and coordinates `x=10.0, y=0.0, z=5.5`
  - **Then** the desk is created with status `DISPONIVEL` and a unique, immutable `qr_code_hash` is generated.

- **AC-2: Reserve Desk with Flexible Time Slot**
  - **Given** an authenticated employee and an available desk
  - **When** POST `/api/v1/bookings` is called with `desk_id`, `start_time=2026-10-01T09:00:00Z` and `end_time=2026-10-01T17:00:00Z`
  - **Then** a booking is created with status `PENDENTE_CHECKIN` and `checkin_deadline` set to `2026-10-01T09:30:00Z`.

- **AC-3: Successful Physical Check-in via QR-Code**
  - **Given** an active booking in `PENDENTE_CHECKIN` status within the valid window
  - **When** POST `/api/v1/bookings/{id}/checkin` is called with the matching desk `qr_code_hash`
  - **Then** the booking status changes to `CHECKED_IN`, recording `checked_in_at` timestamp.

### Input & Validation Scenarios
- **AC-4: Overlapping Booking Rejection**
  - **Given** an existing active booking for Desk 1 from 10:00 to 14:00
  - **When** another booking is requested for Desk 1 from 12:00 to 16:00
  - **Then** the request is rejected with HTTP 409 Conflict and code `BOOKING_OVERLAP`.

- **AC-5: Invalid QR-Code Rejection on Check-in**
  - **Given** an active booking for Desk 1
  - **When** check-in is attempted with the QR hash of Desk 2 or an invalid hash
  - **Then** the request is rejected with HTTP 400 Bad Request and code `INVALID_QR_CODE`.

### Edge Cases & Exceptions (Resilience)
- **AC-6: Auto-Release Scheduler Expiration**
  - **Given** a booking with `start_time` more than 30 minutes in the past and status `PENDENTE_CHECKIN`
  - **When** the auto-release scheduler cycle runs
  - **Then** the booking status transitions to `EXPIRADA_NO_SHOW` and the desk becomes available for new bookings.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `start_time` | Future ISO-8601 (`2026-10-01T09:00:00Z`) | Past dates, `start_time >= end_time` |
| `qr_code_hash` | Exact 64-char hex or UUID string | Empty, altered hash, non-matching baia |
| `desk.status` | `DISPONIVEL`, `RESERVADA`, `OCUPADA`, `MANUTENCAO` | Invalid enum string |
| `role` | `admin`, `colaborador` | `guest`, `supergod` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Linter | `uv run ruff check backend` | 0 errors |
| Test Suite | `uv run pytest backend/tests -v` | 100% pass |
| SDD Integrity | `node .agents/scripts/verify-sdd-integrity.js` | 100% pass |
