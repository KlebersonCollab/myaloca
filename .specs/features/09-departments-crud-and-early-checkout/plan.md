# Feature Plan: CRUD de Departamentos e Liberação Antecipada de Reservas Confirmadas

## 1. Visão Geral
Esta funcionalidade aborda duas necessidades críticas do ecossistema MyAloca:
1. **Governança Organizacional por Departamentos**: Gestão centralizada de departamentos corporativos (Engenharia, Produto, Financeiro, etc.) com CRUD completo, padronização de códigos/siglas e vínculo com usuários e empresas.
2. **Ciclo de Vida Flexível de Reservas (Liberação Antecipada)**: Capacidade de o colaborador cancelar uma reserva pendente ou liberar imediatamente uma reserva em andamento (`CHECKED_IN`) caso saia do escritório mais cedo, desocupando a baia no 3D e liberando o horário para outros colegas agendarem sem conflito.

## 2. Escopo da Solução

### 2.1 Backend
- **Modelo de Dados (`Department`)**:
  - Nova entidade `Department` em `app/models/department.py` com `id`, `name`, `code`, `description`, `company_id`, `is_active`, `created_at`.
  - Extensão do modelo `User` para incluir `department_id` como foreign key com relacionamento para `Department`, preservando compatibilidade com `department` textual.
- **Schemas Pydantic (`app/schemas/department.py`)**:
  - `DepartmentCreate`, `DepartmentUpdate`, `DepartmentResponse`.
- **Serviço e Endpoints (`/api/v1/departments`)**:
  - `GET /api/v1/departments`: Listagem de departamentos com filtros por empresa, status e busca.
  - `GET /api/v1/departments/{id}`: Detalhes do departamento com contagem de membros.
  - `POST /api/v1/departments`: Cadastro de novo departamento (admin/gestor).
  - `PUT /api/v1/departments/{id}`: Atualização de departamento (admin/gestor).
  - `DELETE /api/v1/departments/{id}`: Exclusão com proteção referencial (`DEPARTMENT_HAS_USERS`).
- **Aprimoramento de Liberação de Reservas (`cancel_booking`)**:
  - Atualização do método `cancel_booking` em `app/services/booking_service.py` para permitir que o dono da reserva cancele tanto reservas `PENDENTE_CHECKIN` quanto `CHECKED_IN`.
  - Ao cancelar uma reserva `CHECKED_IN`:
    - Ajusta `end_time = min(end_time, now)` para liberar o tempo residual para outros usuários.
    - Define `status = "FINALIZADA"` (com nota de saída antecipada) ou `"CANCELADA_USUARIO"`.
    - Define a baia como `DISPONIVEL` imediatamente.
  - Criação do endpoint específico `POST /api/v1/bookings/{id}/checkout` (ou integração direta em `/cancel`) para encerramento antecipado.

### 2.2 Frontend
- **Serviço de API (`frontend/src/services/api.ts`)**:
  - Métodos CRUD completos em `api.departments`.
  - Método `api.bookings.checkout` e aprimoramento de `api.bookings.cancel`.
- **Interface de Gestão de Departamentos (`AdminUsersView.vue`)**:
  - Aba de alternância: `[ Colaboradores & Cargos ]` | `[ Departamentos ]`.
  - Grid/Tabela com departamentos cadastrados, siglas, descrição, contagem de membros e ações (Editar, Excluir).
  - Modal de cadastro e edição de departamento com validação.
  - Dropdown dinâmico de departamentos nos formulários de criação/edição de usuário e perfil (`AuthView.vue`).
- **Interface de Cancelamento e Saída Antecipada (`MyBookingsView.vue`)**:
  - Adição de botão **"Cancelar Reserva"** em reservas `PENDENTE_CHECKIN`.
  - Adição de botão **"Liberar Baia / Saída Antecipada"** em reservas `CHECKED_IN`.
  - Diálogos de confirmação com mensagens claras sobre a desocupação imediata da estação.

## 3. Riscos e Mitigações
- **Proteção Referencial**: Impedir exclusão de departamentos com usuários associados via erro `DEPARTMENT_HAS_USERS`.
- **Colisão de Horários**: Ao liberar a baia mais cedo, encurtar `end_time` para `now` garante que futuras reservas para o mesmo dia e baia sejam aceitas pelo algoritmo de overlap.
