# Executive Technical Map: MyAloca

## Visão Geral Técnica
O **MyAloca** é arquitetado como uma aplicação desacoplada de alto desempenho composta por:
1. **Backend**: FastAPI Assíncrono com SQLAlchemy 2.0 Async, Pydantic v2, Alembic e SQLite/PostgreSQL dual-driver.
2. **Frontend**: SPA moderna (React + Vite + TypeScript + Tailwind CSS) com renderizador WebGL 3D em Three.js / React Three Fiber para o layout do escritório, avatares e interação de agendamento em tempo real.
3. **Serviços de Suporte**:
   - **QR Code Engine**: Geração de tokens imutáveis e renderização em alta fidelidade para impressão física em mesas.
   - **Auto-Release Scheduler**: Worker periódico assíncrono para cancelamento automático de reservas sem check-in até o horário limite.

## Matriz de Camadas e Responsabilidades
| Camada | Tecnologia | Responsabilidade Principal |
| :--- | :--- | :--- |
| **API Endpoints** | FastAPI, APIRouter | Roteamento HTTP REST, serialização e validação de DTOs |
| **Domain Services** | Python 3.12+ Async | Lógica de reserva, validação de regras de check-in, no-show |
| **Persistência** | SQLAlchemy 2.0 Async | Modelagem ORM, queries assíncronas, constraints de unicidade |
| **Banco de Dados** | SQLite (`aiosqlite`) / PostgreSQL (`asyncpg`) | Armazenamento relacional com suporte dual transparente |
| **Agendador** | APScheduler Async | Execução da varredura periódica de reservas expiradas |
| **Segurança** | JWT Bearer, Argon2 / Bcrypt | Autenticação, autorização baseada em roles (`admin`, `colaborador`) |
| **Canvas 3D** | Three.js / @react-three/fiber | Renderização interativa do escritório 3D com avatares e status |
| **Design System** | Tailwind CSS (Linear Dark) | Tokens de cor, tipografia e espaçamentos definidos em `DESIGN.md` |

## Comandos Operacionais & Sensores
- **Execução do Backend**: `uv run uvicorn app.main:app --reload --port 8000`
- **Execução dos Testes**: `uv run pytest -v`
- **Linters**: `uv run ruff check .`
- **Integridade SDD**: `node .agents/scripts/verify-sdd-integrity.js`
