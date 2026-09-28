# Roadmap do Projeto: MyAloca

## Visão Geral de Marcos (Milestones)

### Milestone 1: Fundação Backend & Arquitetura de Dados (Em Progresso)
- [ ] M1.1: Estrutura FastAPI Async com SQLAlchemy 2.0 e migrações Alembic
- [ ] M1.2: Suporte dual a banco de dados (SQLite `aiosqlite` para dev local e PostgreSQL `asyncpg` para prod)
- [ ] M1.3: Módulo de Autenticação JWT com papéis (Admin/Gestor e Colaborador) e perfis com upload de foto
- [ ] M1.4: CRUD de Zonas e Baias com coordenadas espaciais 3D `(x, y, z)`
- [ ] M1.5: Gerador de QR-Code criptográfico imutável por baia com endpoint de exportação

### Milestone 2: Motor de Agendamento, Check-in & No-Show Auto-Release
- [ ] M2.1: Sistema de reserva antecipada com detecção de conflitos de horário/baia
- [ ] M2.2: Endpoint seguro de Check-in presencial via leitura do payload do QR Code físico
- [ ] M2.3: Worker/Scheduler em background assíncrono para cancelamento automático de reservas sem check-in (tolerância configurável)
- [ ] M2.4: Testes automatizados assíncronos (pytest-asyncio) para todos os fluxos críticos de reserva e liberação

### Milestone 3: Frontend Moderno com Canvas 3D do Escritório
- [ ] M3.1: Setup da aplicação Frontend (React + Vite + TypeScript + Tailwind CSS) aderente ao design system Linear de `DESIGN.md`
- [ ] M3.2: Renderizador 3D do escritório (Three.js / React Three Fiber) com baias tridimensionais, iluminação e controle orbital
- [ ] M3.3: Exibição dinâmica de ocupação: avatares 3D e badges com foto de perfil do usuário ocupando a baia reservada
- [ ] M3.4: Fluxo de reserva com um clique diretamente no modelo 3D
- [ ] M3.5: Leitor/Scanner de QR Code no front-end para validação de check-in na baia

### Milestone 4: Painel Administrativo de Gestão e Exportação de QR Codes
- [ ] M4.1: Painel do gestor para cadastro e posicionamento interativo das baias no mapa
- [ ] M4.2: Exportação de fichas de baias e QR-Codes prontos para impressão física (PDF / PNG em alta resolução)
- [ ] M4.3: Painel de métricas de ocupação e taxa de no-show
