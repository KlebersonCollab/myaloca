# Technology Stack

## Core Language & Runtime
- **Backend Language**: Python 3.12+ / 3.14 (gerenciado via `uv`)
- **Backend Framework**: FastAPI (Async ASGI com Uvicorn)
- **Database ORM**: SQLAlchemy 2.0 (Declarative Base, Mapped Type Annotations, AsyncSession)
- **Database Drivers**:
  - `aiosqlite` para desenvolvimento local ágil, portátil e zero-configuração
  - `asyncpg` para produção enterprise escalável com PostgreSQL
- **Database Migrations**: Alembic
- **Validation & Serialization**: Pydantic v2
- **Authentication**: Python-JOSE / PyJWT (JWT Bearer) + Passlib / Pwdlib (Bcrypt / Argon2)
- **QR Code Engine**: `qrcode[pil]` para geração de matrizes e exportação em PNG de alta resolução
- **Scheduler**: APScheduler assíncrono para rotina periódica de auto-release de no-shows
- **Frontend Stack**: Vue 3 + Vite + TypeScript + Tailwind CSS + TresJS / Three.js + Lucide Icons (alinhado a `DESIGN.md`)

## Dependencies
- **Backend Production**:
  - `fastapi`: `^0.115.0` — API REST assíncrona
  - `uvicorn[standard]`: `^0.32.0` — Servidor ASGI de alta performance
  - `sqlalchemy[asyncio]`: `^2.0.35` — ORM assíncrono moderno
  - `aiosqlite`: `^0.20.0` — Driver SQLite assíncrono para desenvolvimento
  - `asyncpg`: `^0.30.0` — Driver PostgreSQL assíncrono para produção
  - `alembic`: `^1.13.0` — Controle de migrações de banco de dados
  - `pydantic`: `^2.9.0` — Validação e tipagem de dados
  - `pydantic-settings`: `^2.5.0` — Gerenciamento de configurações por variáveis de ambiente
  - `pyjwt`: `^2.9.0` — Emissão e validação de tokens JWT
  - `pwdlib[argon2]`: `^0.2.0` — Hashing seguro de senhas
  - `python-multipart`: `^0.0.12` — Suporte a upload de fotos de perfil e avatares
  - `qrcode[pil]`: `^8.0` — Geração e renderização de QR Codes
  - `apscheduler`: `^3.10.4` — Agendamento de tarefas em background para auto-release
- **Backend Development & Tooling**:
  - `pytest`: `^8.3.0` — Runner de testes
  - `pytest-asyncio`: `^0.24.0` — Testes assíncronos para FastAPI e SQLAlchemy
  - `httpx`: `^0.27.0` — Cliente HTTP assíncrono para testes de integração com `AsyncClient`
  - `ruff`: `^0.6.0` — Linter e formatador ultrarrápido em Rust

## Testing Infrastructure
- **Framework**: Pytest + pytest-asyncio + HTTPX AsyncClient
- **Sensor Commands**:
  - Lint: `uv run ruff check .`
  - Format: `uv run ruff format --check .`
  - Test: `uv run pytest`
  - SDD Integrity: `node .agents/scripts/verify-sdd-integrity.js`
