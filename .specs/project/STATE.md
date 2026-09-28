# Project State & Context

## 🏁 Session Status
- **Current Task**: Definição da arquitetura canônica inicial, validação das especificações SDD e alinhamento com o usuário sobre o frontend e modelo de dados.
- **Progress**: 15% (Fundação das especificações e mapeamento da stack).
- **Next Steps**:
  1. Confirmar com o usuário as decisões arquiteturais da stack (FastAPI Async + SQLAlchemy 2.0 + SQLite/Postgres + React R3F ou Vue TresJS).
  2. Implementar a estrutura base do Backend FastAPI com `uv`.
  3. Configurar SQLAlchemy 2.0 Async, schemas Pydantic v2 e autenticação.
  4. Implementar endpoints de Baias, QR-Codes e Agendamentos com auto-release.

## 💡 Decisions Log
- **2026-09-28 - Backend Stack**: FastAPI Async escolhido com SQLAlchemy 2.0 (`aiosqlite` para dev local e `asyncpg` para PostgreSQL em produção via URL de conexão desacoplada).
- **2026-09-28 - Check-in Físico via QR Code**: Cada baia tem um token UUIDv4 / HMAC estável embutido no QR Code, impresso e colado na bancada. O check-in presencial compara o hash lido no local com o hash da baia.
- **2026-09-28 - Motor de No-Show Auto-Release**: Background scheduler assíncrono executa periodicamente verificando reservas `PENDENTE_CHECKIN` cujo horário de tolerância (ex: 30 min após início) expirou, revertendo a baia para `DISPONIVEL`.
- **2026-09-28 - Visualizador 3D**: Uso de Three.js com visualização orbital, posições espaciais `(x, y, z)` para cada baia, e marcadores com foto/avatar do colaborador ocupando a posição.

## 🚧 Active Blockers
- N/A.

## ❄️ Deferred Ideas / Icebox
- Integração com Google Workspace / Microsoft 365 para sincronização de calendário de dias presenciais.
- Sensores IoT físicos em mesas (sensores de presença por ultrassom/pressão) como alternativa de hardware ao QR Code.

## ⚠️ Known Technical Debts
- N/A (Greenfield).
