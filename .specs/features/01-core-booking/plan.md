# Plan: Core Booking, Desks & QR-Code Check-in System

## 1. Problem Statement & Motivation
Em escritórios com regime de trabalho híbrido, a falta de controle sobre ocupação de baias gera dois problemas críticos:
1. **Reservas Fantasmas (No-Shows)**: Colaboradores reservam baias com antecedência e não comparecem, impedindo que outros utilizem o espaço.
2. **Falta de Validação Presencial**: Dificuldade de comprovar se quem reservou está de fato trabalhando no local.

O **MyAloca Core** resolve isso fornecendo o núcleo da API em FastAPI Async com cadastro de baias, QR Codes imutáveis únicos para validação física e motor de liberação automática de assentos caso o check-in não seja realizado dentro da janela de tolerância de 30 minutos após o início da reserva.

## 2. Scope & Boundaries
- **In Scope**:
  - Configuração do projeto Python backend com `uv`, FastAPI, SQLAlchemy 2.0 Async e Pydantic v2.
  - Suporte dual a banco de dados: SQLite (`aiosqlite`) para dev/testes locais e PostgreSQL (`asyncpg`) para produção.
  - Autenticação e Perfis: Registro, login com JWT Bearer, controle de acesso (`admin`/`gestor` vs `colaborador`), campos para foto de perfil e avatar 3D.
  - Gestão de Espaços: CRUD de Zonas/Andares e Baias com coordenadas espaciais 3D `(x, y, z)`.
  - Motor de QR-Code: Geração de token imutável criptografado por baia e exportação de imagem PNG para impressão física.
  - Motor de Agendamento: Reserva por horário flexível (`start_time`, `end_time`) com prevenção atômica de conflitos.
  - Validação de Check-in: Endpoint para registrar presença através da leitura do payload do QR Code físico.
  - Scheduler de Auto-Release: Worker assíncrono em background que cancela automaticamente reservas sem check-in após `start_time + 30 min` (no-show).
  - Testes automatizados assíncronos cobrindo todo o ciclo de vida.
- **Out of Scope**:
  - Interface visual 3D WebGL (coberta na Feature 02: `frontend-3d-canvas`).
  - Integração com catracas de acesso físico ou SSO SAML corporativo.

## 3. High-Level Approach
- Criar a aplicação backend estruturada de acordo com as convenções de Clean Architecture e separação de responsabilidades.
- Utilizar `AsyncEngine` e `async_sessionmaker` do SQLAlchemy 2.0 com `aiosqlite` por padrão, parametrizável via `DATABASE_URL`.
- Implementar o scheduler assíncrono desacoplado via APScheduler ou `asyncio.create_task` contínuo executando queries de detecção de no-shows baseadas em timestamps.

## 4. Dependencies & Prerequisites
- Python 3.12+ / 3.14 com gerenciador de pacotes `uv`.
- Node.js para validação do sensor canônico SDD.

## 5. Architectural Decision Records (ADRs)
- `.specs/project/ADRs/0001-stack-and-architecture.md`: Define a escolha de FastAPI Async, SQLAlchemy 2.0 dual-driver, regras de tolerância de 30 minutos e motor de QR Codes.
