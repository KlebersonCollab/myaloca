# Feature Plan: Cancelamento Administrativo e Liberação de Baias Reservadas

## 1. Visão Geral
Esta funcionalidade permite que gestores e administradores cancelem e liberem baias reservadas ou ocupadas por outros colaboradores, atendendo a situações práticas em que o colaborador avisa presencialmente ou por mensagem que desocupou o espaço ou que não poderá comparecer. A liberação desocupa a estação imediatamente na maquete 3D e disponibiliza o assento e horário para novos agendamentos sem colisão.

## 2. Escopo da Solução

### 2.1 Backend
- **Endpoint Administrativo (`/api/v1/desks/{id}/release`)**:
  - Implementação em `backend/app/api/v1/endpoints/desks.py` com dependência `get_current_admin` (`admin` e `gestor`).
  - Identifica qualquer reserva ativa (`PENDENTE_CHECKIN` ou `CHECKED_IN`) associada à baia.
  - Finaliza/cancela a reserva truncando `end_time = now` e define `desk.status = "DISPONIVEL"`.
  - Retorna a baia atualizada.

### 2.2 Frontend
- **Serviço de API (`frontend/src/services/api.ts`)**:
  - Adição do método `api.desks.release(deskId)` em `api.desks`.
- **Painel Administrativo de Baias (`frontend/src/views/AdminDesksView.vue`)**:
  - Adição de botão **"Liberar"** na coluna de ações da tabela de baias para estações com status `RESERVADA` ou `OCUPADA`.
  - Modal de confirmação seguro de liberação administrativa.
- **Modal da Maquete 3D (`frontend/src/components/BookingModal.vue`)**:
  - Para baias ocupadas ou reservadas, caso o usuário logado seja `admin`, `gestor` ou o próprio ocupante, exibir botão destacado **"Liberar Baia / Cancelar Reserva"**.
  - Liberação com recarregamento síncrono da maquete WebGL.

## 3. Riscos e Mitigações
- **Segurança de Acesso (RBAC)**: Apenas administradores e gestores (ou o próprio titular) podem liberar baias reservadas de terceiros. Colaboradores comuns têm permissão negada (`403 Forbidden`).
- **Consistência de Estado**: A liberação trunca a reserva ativa para que futuros cálculos de sobreposição (`BOOKING_OVERLAP`) não encontrem colisão.
