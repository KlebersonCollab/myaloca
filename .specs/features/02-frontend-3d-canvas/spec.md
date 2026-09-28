# Specification: Frontend Vue 3 + 3D Office Canvas & Hot-Desking Experience

## 1. User Stories
- **US-1**: As a `Colaborador`, I want to navigate the 3D office floor plan using mouse/touch orbit controls, so that I can explore desk locations and view where my teammates are seated.
- **US-2**: As a `Colaborador`, I want to click on an available 3D desk to view its equipment and reserve it for a flexible time slot, so that I can secure my workstation.
- **US-3**: As a `Colaborador`, I want to see the photos and avatars of colleagues floating on their reserved desks, so that I can choose to sit next to people I collaborate with.
- **US-4**: As a `Colaborador`, I want to use my device's camera to scan the desk's physical QR Code, so that I can check in and confirm my physical presence.
- **US-5**: As a `Gestor`, I want to view all desks, inspect occupancy metrics, and download printable QR Code stickers for physical placement.

## 2. Business Rules & Invariants
- **BR-1**: The 3D canvas must accurately reflect backend coordinates `(pos_x, pos_y, pos_z)` and `rotation_y`.
- **BR-2**: Desks with status `DISPONIVEL` must be visually distinct (emerald green `#27a644`) from `RESERVADA` (amber `#eab308`) and `OCUPADA` (Linear lavender `#5e6ad2`).
- **BR-3**: When a desk is reserved or occupied, the occupant's avatar and name badge must float directly above the desk surface.
- **BR-4**: Check-in scanner must decode `myaloca://desk/{id}?hash={hash}&code={code}` and dispatch check-in API request.
- **BR-5**: All UI surfaces must strictly adhere to the Linear Dark palette and typography defined in `DESIGN.md`.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: 3D Scene Initialization and Desk Mesh Rendering**
  - **Given** an authenticated user on the 3D Office page
  - **When** the 3D canvas mounts and fetches `/api/v1/bookings/3d-office`
  - **Then** desks are rendered at their exact 3D coordinates with ambient lighting and OrbitControls.

- **AC-2: Occupant Avatar Display**
  - **Given** a desk with an active booking and an occupant with photo/avatar
  - **When** viewing the 3D scene
  - **Then** a billboard badge displays the collaborator's avatar/photo and name directly above the desk.

- **AC-3: Interactive Desk Click & Booking Flow**
  - **Given** a user clicks on an available green desk in the 3D canvas
  - **When** the booking modal opens and the user selects a time range and confirms
  - **Then** the booking is created via API, the desk turns amber/reserved, and the user's avatar appears on it.

- **AC-4: QR-Code Physical Check-in**
  - **Given** a user with a pending reservation
  - **When** the user opens the QR check-in scanner and reads the desk's QR code
  - **Then** check-in is validated by the backend, the desk turns purple/occupied, and a confirmation toast is shown.

### Input & Validation Scenarios
- **AC-5: Time Range Validation in Booking Modal**
  - **Given** a user selects an end time earlier than start time
  - **When** attempting to confirm
  - **Then** the form prevents submission with an inline validation alert.

### Edge Cases & Exceptions (Resilience)
- **AC-6: Backend Disconnection Fallback**
  - **Given** the FastAPI backend is temporarily unreachable
  - **When** loading the 3D canvas
  - **Then** an informative banner is displayed with a retry button without crashing the WebGL context.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| Camera Zoom | Distance between 5.0 and 50.0 units | Distance <= 0.1 (clipping) |
| QR Code String | `myaloca://desk/1?hash=...` | Malformed URL, empty string |
| Desk Click Raycast | Mesh intersects with mouse vector | Click outside canvas or on empty floor |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Build Sensor | `npm run build` (in frontend/) | Exit code 0, dist/ generated |
| SDD Integrity | `node .agents/scripts/verify-sdd-integrity.js` | 100% pass |

## 6. UI & Design System Tokens (Linear Dark from DESIGN.md)
- **Background Canvas**: `#010102` (deepest dark)
- **Surfaces**: Surface-1 `#0f1011`, Surface-2 `#141516`, Surface-3 `#18191a`
- **Hairlines**: `#23252a`, Strong `#34343a`
- **Accents**: Primary `#5e6ad2`, Primary Hover `#828fff`, Success `#27a644`
- **Text (Ink)**: Main `#f7f8f8`, Muted `#d0d6e0`, Subtle `#8a8f98`
- **Typography**: Sans-serif (Inter / SF Pro Display) with tight negative tracking on headlines
