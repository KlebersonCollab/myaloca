# Plan: Remoção Segura de Baias e Governança de Dependências

## 1. Problem Statement & Motivation
O gestor de facilities precisa ter total flexibilidade para remover baias ou salas cadastradas erroneamente ou desativadas fisicamente no escritório. No entanto, não havia no sistema a funcionalidade de exclusão de estações, nem no backend nem na interface do gestor. É indispensável disponibilizar a opção de exclusão com proteções para impedir a remoção de estações que tenham reservas ativas em andamento.

## 2. Scope & Boundaries
- **In Scope**:
  - Backend: Método `DeskService.delete_desk` que verifica existência de reservas ativas (`PENDENTE_CHECKIN`, `CHECKED_IN`) e limpa reservas históricas antes de deletar a baia.
  - Backend: Endpoint `DELETE /api/v1/desks/{id}` protegido para papel `gestor` e `admin`.
  - Backend: Testes automatizados pytest para deleção com sucesso, rejeição quando há reserva ativa, e rejeição para usuário colaborador.
  - Frontend: Método `api.desks.delete(id)` no cliente de API.
  - Frontend: Ação de exclusão com diálogo de confirmação seguro no painel administrativo (`AdminDesksView.vue`).
- **Out of Scope**:
  - Exclusão em lote sem confirmação individual.

## 3. High-Level Approach
1. Implementar método seguro em `DeskService` e rota `DELETE /api/v1/desks/{id}` no FastAPI.
2. Adicionar testes unitários assíncronos no pytest.
3. Expor método no serviço frontend `api.desks.delete`.
4. Adicionar botão e modal de confirmação de exclusão na tabela e nos detalhes da baia no `AdminDesksView.vue`.

## 4. Dependencies & Prerequisites
- Módulo de Desks e Bookings existentes.

## 5. Architectural Decision Records (ADRs)
- ADR 0004: Governança de Remoção de Baias e Proteção de Reservas Ativas
