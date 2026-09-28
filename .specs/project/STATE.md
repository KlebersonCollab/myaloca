# Project State & Context

## 🏁 Session Status
- **Current Task**: Conclusão da Feature 01 (Backend FastAPI Async Core, SQLAlchemy 2.0 dual SQLite/PostgreSQL, Autenticação JWT, Baias 3D, Geração de QR Code imutável, Agendamento por horário flexível e Scheduler assíncrono de Auto-Release por No-Show). Preparação para a Feature 02 (Frontend SPA Vue 3 + TresJS / Three.js).
- **Progress**: 50% (Backend completo com 15 testes automatizados aprovados e cobertura total das regras de negócio).
- **Next Steps**:
  1. Apresentar ao usuário a arquitetura implementada, demonstrar os endpoints REST e a documentação interativa OpenAPI/Swagger.
  2. Implementar a Feature 02: Frontend Vue 3 + Vite + TypeScript + Tailwind CSS (Linear Dark) + TresJS / Three.js com visualização 3D orbital, avatares nas baias e leitor de QR Code.

## 💡 Decisions Log
- **2026-09-28 - Backend Stack**: FastAPI Async com SQLAlchemy 2.0 (`aiosqlite` para dev local e `asyncpg` para PostgreSQL em produção via URL de conexão desacoplada).
- **2026-09-28 - Frontend Stack**: Vue 3 + Vite + TypeScript + Tailwind CSS + TresJS / Three.js (escolhido pelo usuário para fluidez e alinhamento à identidade Linear Dark de `DESIGN.md`).
- **2026-09-28 - Check-in Físico via QR Code**: Cada baia tem um token criptográfico imutável único gerado pelo gestor. A leitura presencial via leitor de câmera envia o token para validação.
- **2026-09-28 - Motor de No-Show Auto-Release**: Background scheduler assíncrono executa periodicamente verificando reservas `PENDENTE_CHECKIN` com tolerância de 30 minutos após o início, cancelando reservas abandonadas e liberando assentos.
- **2026-09-28 - Projeção 3D do Escritório**: Endpoint `/api/v1/bookings/3d-office` projeta coordenadas `(x, y, z)`, rotação e dados do ocupante (avatar, foto, nome) para montagem direta da cena WebGL.

## 🚧 Active Blockers
- N/A.

## ❄️ Deferred Ideas / Icebox
- Integração com Google Workspace / Microsoft 365 para sincronização de calendário de dias presenciais.
- Sensores IoT físicos em mesas (sensores de presença por ultrassom/pressão) como alternativa de hardware ao QR Code.

## ⚠️ Known Technical Debts
- N/A.
