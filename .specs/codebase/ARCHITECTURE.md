# System Architecture: MyAloca

## Directory Organization
```text
myaloca/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py         # Login, registro, token refresh
│   │   │   │   │   ├── users.py        # Perfil, fotos, avatares
│   │   │   │   │   ├── zones.py        # Zonas/Andares do escritório
│   │   │   │   │   ├── desks.py        # Baias, coordenadas 3D, QR Codes
│   │   │   │   │   └── bookings.py     # Reservas, check-in, histórico
│   │   │   │   └── router.py           # Agrupamento das rotas da v1
│   │   ├── core/
│   │   │   ├── config.py               # Settings (Pydantic), DATABASE_URL, tolerâncias
│   │   │   ├── security.py             # JWT, hash de senha, validação de tokens
│   │   │   └── scheduler.py            # Async APScheduler (Auto-release No-Show)
│   │   ├── db/
│   │   │   ├── base.py                 # DeclarativeBase e metadados
│   │   │   ├── session.py              # async_engine e async_sessionmaker
│   │   │   └── init_db.py              # Seed inicial (Admin, Zonas, Baias de exemplo)
│   │   ├── models/                     # Modelos SQLAlchemy 2.0 (User, Zone, Desk, Booking)
│   │   ├── schemas/                    # Schemas Pydantic v2 (Request, Response, Filter)
│   │   ├── services/                   # Regras de negócio (BookingService, DeskService, QRCodeService)
│   │   └── main.py                     # Entrypoint FastAPI, CORS, middlewares e lifecycle
│   ├── tests/                          # Testes assíncronos (pytest + httpx AsyncClient)
│   ├── alembic/                        # Histórico de migrações
│   └── pyproject.toml                  # Configuração do projeto gerenciada pelo uv
└── frontend/                           # Aplicação Web (Vue 3 + Vite + TresJS / Three.js)
    ├── src/
    │   ├── components/                 # Componentes de UI (Cards, Modals, QR Reader)
    │   ├── canvas3d/                   # Cena 3D TresJS / Three.js (OfficeFloor, DeskMesh, AvatarMesh)
    │   ├── views/                      # Páginas/Views (Dashboard, Mapa 3D, Minhas Reservas, Gestor)
    │   └── services/                   # Chamadas de API HTTP
    └── package.json
```

## Architectural Patterns
- **Clean Architecture & Separation of Concerns**:
  - `Endpoints`: Apenas recebem requisições HTTP, validam schemas com Pydantic e delegam para services.
  - `Services`: Contêm todas as regras de negócio (conflitos de reserva, validação de tolerância, no-show, geração de QR Code).
  - `Models`: Entidades mapeadas para o banco de dados relacional via SQLAlchemy 2.0.
  - `Core`: Configurações centrais e scheduler de processos em background.
- **Dual Database Strategy**:
  - `DATABASE_URL` determina dinamicamente o dialeto.
  - SQLite: `sqlite+aiosqlite:///./myaloca.db`
  - PostgreSQL: `postgresql+asyncpg://user:pass@host:5432/myaloca`
- **Scheduler de Auto-Release**:
  - Processo periódico assíncrono executado a cada minuto para buscar reservas `PENDENTE_CHECKIN` cujo tempo limite de tolerância foi excedido e convertê-las para `EXPIRADA_NO_SHOW`.

## Boundary Rules
- Nenhum endpoint pode realizar queries SQL diretas ou conter lógica de regras de negócio sem passar pelo Service.
- A validação do QR Code exige verificação do hash criptográfico único registrado na baia.
- Apenas usuários com role `admin` ou `gestor` podem criar/alterar baias ou exportar lotes de QR codes.
