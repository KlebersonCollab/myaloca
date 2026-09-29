# ADR 0007: CRUD de Departamentos e Liberação Antecipada de Reservas Confirmadas

## Status
Accepted

## Data
2026-09-28

## Contexto
1. **Estrutura Organizacional por Departamentos**:
   - Atualmente, o modelo `User` possui um atributo livre de texto `department`. No entanto, gestores corporativos não têm capacidade de padronizar, listar, criar, editar ou desativar departamentos formais (ex: Engenharia, Design, Operações, Recursos Humanos).
   - Departamentos devem ter código/sigla, descrição, status ativo e vínculo opcional com a empresa (`Company`), servindo como base para organização de equipes, relatórios e filtros de alocação de baias.

2. **Liberação Antecipada / Checkout de Reserva Confirmada**:
   - Quando um colaborador confirma presença via QR Code (`CHECKED_IN`), a reserva permanece bloqueando a baia até o horário final previsto (`end_time`).
   - Caso o colaborador termine suas atividades ou saia do escritório mais cedo, ele não possui mecanismo na interface para encerrar o uso da baia.
   - Isso gera desperdício de espaço híbrido, pois a baia continua marcada como ocupada na maquete 3D e o sistema rejeita agendamentos de outros colegas por sobreposição de horário (`BOOKING_OVERLAP`).

## Decisão Arquitetural

1. **CRUD Completo de Departamentos (`/api/v1/departments`)**:
   - Criação da entidade `Department` (`backend/app/models/department.py`) vinculada à `Company`.
   - Adição de `department_id` na entidade `User` com preservação retrocompatível da coluna `department`.
   - Endpoints de CRUD protegidos por perfil (`admin` / `gestor`):
     - `GET /api/v1/departments`: Listagem com filtros por empresa, status e busca textual.
     - `POST /api/v1/departments`: Cadastro de novo departamento.
     - `PUT /api/v1/departments/{id}`: Atualização de dados.
     - `DELETE /api/v1/departments/{id}`: Exclusão com proteção referencial (`DEPARTMENT_HAS_USERS` se houver usuários ativos vinculados).
   - Interface no frontend:
     - Aba dedicada de Departamentos no painel corporativo (`AdminUsersView.vue`) com métricas e gestão de registros.
     - Integração de seleção de departamento nos modais de usuário e perfil (`AuthView.vue`).

2. **Cancelamento e Liberação Antecipada de Reservas (`cancel_booking` & `early checkout`)**:
   - Habilitação de cancelamento pelo próprio usuário para reservas tanto em estado `PENDENTE_CHECKIN` quanto `CHECKED_IN`.
   - Para reservas com status `CHECKED_IN`:
     - O encerramento antecipado ajusta `end_time = min(end_time, now)` para liberar imediatamente a janela de tempo restante para novos agendamentos sem colisão.
     - Atualiza o status da reserva para `FINALIZADA` (ou `CANCELADA_USUARIO`).
     - Altera imediatamente o status da baia para `DISPONIVEL`, removendo o avatar do colaborador da maquete 3D.
   - Interface em `MyBookingsView.vue`:
     - Adição do botão "Cancelar Reserva" para reservas pendentes.
     - Adição do botão "Liberar Baia / Saída Antecipada" para reservas com check-in realizado.

## Consequências
- **Positivas**:
  - Otimização imediata da taxa de ocupação do escritório híbrido: baias abandonadas mais cedo ficam disponíveis instantaneamente para outros funcionários.
  - Governança corporativa completa com departamentos cadastrados e padronizados.
  - Eliminação de colisões desnecessárias de reserva após a saída física do colaborador.
- **Negativas / Cuidados**:
  - A integridade da exclusão de departamentos requer validação síncrona para não quebrar referências em usuários.
