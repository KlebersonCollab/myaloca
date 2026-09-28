# MyAloca Backend API

API assíncrona de alta performance desenvolvida em **FastAPI** para gestão, cadastro e agendamento de baias de trabalho em escritórios com regime de trabalho híbrido. Possui validação presencial física via **QR-Codes imutáveis**, **scheduler em background com auto-release de no-show** e suporte a **projeção tridimensional (3D)** com avatares e fotos de perfil dos colaboradores.

---

## 🛠️ Stack Tecnológica

- **Runtime & Linguagem**: Python 3.12+ (gerenciado via [`uv`](https://github.com/astral-sh/uv))
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Async ASGI) & [Uvicorn](https://www.uvicorn.org/)
- **ORM & Persistência**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) Async (`AsyncSession`, `async_sessionmaker`, DeclarativeBase)
- **Suporte Dual a Banco de Dados**:
  - `aiosqlite`: SQLite assíncrono para desenvolvimento ágil, testes e execução local sem dependências externas.
  - `asyncpg`: PostgreSQL assíncrono nativo para produção escalável.
- **Validação & Serialização**: [Pydantic v2](https://docs.pydantic.dev/latest/) com validação de faixas de horário e `email-validator`
- **Autenticação & Segurança**: JWT (PyJWT) + Hashing seguro de senhas com Argon2 ([`pwdlib`](https://github.com/frankie567/pwdlib))
- **Motor de QR Code**: `qrcode[pil]` para renderização de matrizes e exportação em imagem PNG de alta fidelidade
- **Scheduler em Background**: Rotina assíncrona periódica de auto-release de reservas sem check-in (tolerância de 30 min)
- **Testes & Qualidade**: Pytest + pytest-asyncio + HTTPX AsyncClient + Ruff (Linter & Formatter em Rust)

---

## 🏗️ Arquitetura de Pastas

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                     # Injeção de dependências (auth, admin, db)
│   │   └── v1/
│   │       ├── router.py               # Agregador de rotas da versão 1
│   │       └── endpoints/
│   │           ├── auth.py             # Login, registro e perfil (/me)
│   │           ├── zones.py            # CRUD de Zonas / Andares
│   │           ├── desks.py            # Baias, coordenadas 3D e exportação de QR Code
│   │           └── bookings.py         # Reservas, check-in e projeção 3D do escritório
│   ├── core/
│   │   ├── config.py                   # Configurações globais (Pydantic Settings)
│   │   ├── security.py                 # Argon2 e geração de tokens JWT
│   │   └── scheduler.py                # Worker periódico assíncrono para Auto-Release
│   ├── db/
│   │   ├── base.py                     # DeclarativeBase do SQLAlchemy 2.0
│   │   ├── session.py                  # async_engine e async_sessionmaker
│   │   └── init_db.py                  # Seed inicial automático de administradores e baias 3D
│   ├── models/                         # Modelos ORM (User, Zone, Desk, Booking)
│   ├── schemas/                        # DTOs e Schemas Pydantic v2
│   ├── services/                       # Regras de negócio (BookingService, DeskService)
│   └── main.py                         # Entrypoint da aplicação FastAPI e ciclo de vida
├── tests/                              # Suíte de testes automatizados com in-memory SQLite
├── pyproject.toml                      # Gerenciamento de dependências via uv
└── README.md
```

---

## ⚡ Pré-requisitos & Instalação

O projeto utiliza o **[`uv`](https://docs.astral.sh/uv/)**, o gerenciador de pacotes ultrarrápido em Rust para Python.

### 1. Instalar o `uv` (caso ainda não possua)
- **Windows (PowerShell)**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Linux/macOS**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Clonar e Instalar as Dependências
Dentro da pasta `backend/`:

```bash
uv sync --extra dev
```

O `uv` fará automaticamente o download do Python 3.12 (se necessário) e instalará todas as dependências em um ambiente virtual isolado `.venv/`.

---

## 🚀 Executando o Servidor Localmente

Para iniciar a API com recarregamento automático (hot-reload):

```bash
uv run uvicorn app.main:app --reload --port 8000
```

A API estará disponível em:
- **API Base**: [http://localhost:8000](http://localhost:8000)
- **Documentação Interativa Swagger / OpenAPI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentação Alternativa ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Sensor de Healthcheck**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 👥 Credenciais Pré-semeadas (Seed Automático)

Ao inicializar pela primeira vez, o sistema popula automaticamente o banco de dados com dados de teste:

| Papel | E-mail | Senha | Descrição |
| :--- | :--- | :--- | :--- |
| **Admin / Gestor** | `admin@myaloca.com` | `admin123` | Permissão para cadastrar zonas, baias e baixar QR codes |
| **Colaborador** | `colaborador@myaloca.com` | `colab123` | Permissão para reservar baias e realizar check-in presencial |

Também são geradas automaticamente baias de exemplo posicionadas em um grid tridimensional na **Zona Alpha - Open Space** prontas para visualização 3D.

---

## 🔌 Resumo dos Principais Endpoints

### 🔐 Autenticação (`/api/v1/auth`)
- `POST /register`: Registro de novos colaboradores ou gestores
- `POST /login`: Autenticação OAuth2 Password Request, retorna Bearer Token JWT
- `GET /me`: Consulta o perfil do usuário logado (com foto e avatar 3D)
- `PUT /me`: Atualiza dados cadastrais, avatar e senha

### 🏢 Zonas & Andares (`/api/v1/zones`)
- `POST /`: Cadastra nova zona ou andar (requer papel de admin/gestor)
- `GET /`: Lista todas as zonas ativas

### 🪑 Baias & QR Codes (`/api/v1/desks`)
- `POST /`: Cadastra uma baia com coordenadas tridimensionais (`pos_x`, `pos_y`, `pos_z`, `rotation_y`) e flags de equipamento (monitor, docking)
- `GET /`: Lista todas as baias (com filtro opcional por `zone_id`)
- `GET /{id}`: Detalhes de uma baia específica
- `GET /{id}/qrcode`: Gera e exporta o **QR Code físico imutável** em imagem PNG de alta resolução para impressão e fixação na bancada

### 📅 Agendamentos & Presença (`/api/v1/bookings`)
- `POST /`: Cria reserva antecipada por horário flexível (`start_time`, `end_time`) com prevenção atômica de sobreposição de horário (conflitos retornam HTTP 409 `BOOKING_OVERLAP`)
- `POST /{id}/checkin`: **Check-in físico presencial** via leitura do hash do QR Code da baia (valida se o hash confere e se está dentro da janela de tolerância de 30 min)
- `GET /me`: Consulta o histórico de reservas do colaborador autenticado
- `GET /3d-office`: **Endpoint de Projeção Tridimensional**. Retorna todas as baias com suas coordenadas espaciais 3D e, caso ocupada/reservada, o nome, foto de perfil e avatar 3D do colaborador correspondente

---

## ⏱️ Regra de Negócio: Auto-Release No-Show

1. Toda reserva é criada com o status `PENDENTE_CHECKIN` e define um `checkin_deadline = start_time + 30 minutos`.
2. O check-in presencial pode ser realizado a partir de 15 minutos antes do início da reserva até o horário de tolerância (30 min após o início).
3. O worker assíncrono em background [`app.core.scheduler`](file:///F:/Projetos/myaloca/backend/app/core/scheduler.py) executa a cada 60 segundos buscando reservas `PENDENTE_CHECKIN` cujo prazo expirou.
4. Reservas não confirmadas são convertidas automaticamente para `EXPIRADA_NO_SHOW` e a baia é imediatamente liberada como `DISPONIVEL` para outros colegas.

---

## 🧪 Testes Automatizados & Verificação de Qualidade

Para rodar a suíte completa de testes de integração assíncronos:

```bash
uv run pytest -v
```

Para rodar o linter e checagem de código com o Ruff:

```bash
uv run ruff check .
```

Para formatar automaticamente o código:

```bash
uv run ruff format .
```

---

## 🗄️ Alternando para PostgreSQL em Produção

Para utilizar PostgreSQL em produção, basta definir a variável de ambiente:

```bash
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/myaloca
```

Nenhuma modificação de código ou schema é necessária, pois a camada de sessão e queries foi projetada com tipagem universal compatível com ambos os dialetos.
