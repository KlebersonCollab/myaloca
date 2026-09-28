# ADR 0001: Seleção de Stack Tecnológica e Arquitetura do MyAloca

## Status
Accepted

## Contexto
O MyAloca é um sistema corporativo para gestão e agendamento de baias de trabalho em regime híbrido. Os requisitos acordados demandam:
1. Backend assíncrono de alta performance em Python com **FastAPI**.
2. Suporte dual a banco de dados relacional: **SQLite** (`aiosqlite`) para desenvolvimento local e testes ágeis com zero-configuração; e **PostgreSQL** (`asyncpg`) para produção enterprise, orquestrados via **SQLAlchemy 2.0 Async** e **Alembic**.
3. Gestão e agendamento de baias por **horário livre / faixa de horários** (ex: 10:00 às 15:00) com tolerância de check-in de 30 minutos após o início da reserva.
4. Geração de **QR Codes imutáveis** associados a cada baia física para validação presencial no check-in.
5. Liberação automática de baias por **no-show** através de scheduler em background que cancela reservas que não fizeram check-in até `start_time + 30 minutos`.
6. Frontend moderno em **Vue 3 + Vite + TypeScript + Tailwind CSS** com visualização 3D do escritório via **TresJS / Three.js**, exibindo avatares e fotos de perfil dos colaboradores nas baias ocupadas, em conformidade com o design system Linear Dark (`DESIGN.md`).

## Decisão
1. **Backend**: Adotar **FastAPI** com Python 3.12+/3.14 via **uv**, **SQLAlchemy 2.0 Async**, **Pydantic v2** e **APScheduler** assíncrono para o worker de auto-release.
2. **Banco de Dados**: Suporte dual configurável via variável de ambiente `DATABASE_URL`:
   - Dev/Test: `sqlite+aiosqlite:///./myaloca.db`
   - Prod: `postgresql+asyncpg://...`
3. **QR Code Engine**: Criptografia de token imutável por baia com exportação em PNG de alta resolução para impressão física.
4. **Frontend**: Aplicação SPA em **Vue 3 + Vite + TypeScript + Tailwind CSS + TresJS / Three.js**, consumindo a API REST do FastAPI e integrando leitor de QR Code para check-in.

## Consequências
- **Positivas**:
  - Reatividade fluida com a Composition API do Vue 3 e suporte a 3D declarativo com TresJS/Three.js.
  - Conformidade natural com o ecossistema existente e os tokens Linear Dark de `DESIGN.md`.
  - Tolerância de 30 minutos previne reservas fantasmas sem penalizar atrasos razoáveis.
  - Testabilidade completa em ambiente assíncrono.
