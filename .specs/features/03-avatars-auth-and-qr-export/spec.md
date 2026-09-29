# Specification: 3D Avatars, Occupant Visibility, Dedicated Auth UI & QR Code Export

## 1. User Stories
- **US-1**: As a `Colaborador`, I want to clearly see the names and avatars of colleagues floating on their 3D desks, so that I immediately know who is present in the office.
- **US-2**: As a `Colaborador`, I want to hover or click on an occupied desk and see the occupant's photo, department, and booking time.
- **US-3**: As a `Gestor`, I want to click "Exportar PNG" or "Imprimir Adesivo" and immediately download or print the physical QR Code with high resolution without authentication failures.
- **US-4**: As a `User`, I want a dedicated Login and Registration screen where I can sign in, choose my avatar, or view/edit my profile.

## 2. Business Rules & Invariants
- **BR-1**: The 3D scene must render an occupant avatar card with full name and department whenever `desk.status` is `RESERVADA` or `OCUPADA`.
- **BR-2**: Initial demo seed must create active bookings with diverse avatars so the 3D map is populated out-of-the-box.
- **BR-3**: QR Code export must use authenticated binary stream download to prevent HTTP 401 errors.
- **BR-4**: Users can customize their avatar from preset DiceBear styles or enter a custom photo URL.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Visible 3D Avatar Card with Occupant Name**
  - **Given** a desk occupied by "Lucas Desenvolvedor"
  - **When** the 3D canvas loads
  - **Then** a floating card displays the avatar icon and the text "Lucas Desenvolvedor" in white with high contrast.

- **AC-2: Authenticated QR Code Download**
  - **Given** a manager viewing the Desks table
  - **When** clicking "Baixar PNG"
  - **Then** an authenticated request fetches the image blob and triggers browser download of `qrcode-[code].png`.

- **AC-3: Dedicated Authentication & Profile Screen**
  - **Given** an unauthenticated or authenticated user
  - **When** navigating to the Auth/Profile view
  - **Then** the user can log in with credentials, register with avatar selection, or update their profile.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| QR Download | Valid desk id with bearer token | Invalid desk id, missing token |
| Avatar URL | Image URL or DiceBear SVG | Malformed URL string |
| Login Form | Valid email & password | Incorrect password, empty fields |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Backend Pytest | `uv run pytest -v` (in backend/) | 100% pass |
| Frontend Build | `npm run build` (in frontend/) | Exit code 0, dist/ generated |
| SDD Integrity | `node .agents/scripts/verify-sdd-integrity.js` | 100% pass |
