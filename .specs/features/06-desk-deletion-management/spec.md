# Specification: Remoção Segura de Baias e Governança de Dependências

## 1. Feature Overview
Fornece aos gestores a capacidade de remover estações de trabalho ou salas do catálogo do edifício com segurança, garantindo que baias com reservas ativas não sejam excluídas acidentalmente e limpando históricos arquivados de forma limpa.

## 2. Acceptance Criteria (BDD)

### Scenario 1: Exclusão com Sucesso de Baia Sem Reservas Ativas
- **Given** que existe uma baia cadastrada sem nenhuma reserva ou apenas com reservas históricas finalizadas/canceladas,
- **When** um gestor ou administrador requisita a exclusão da baia via `DELETE /api/v1/desks/{id}`,
- **Then** a baia é removida do banco de dados com sucesso retornando HTTP 200/204 e deixa de constar na listagem e na planta 3D.

### Scenario 2: Bloqueio de Exclusão Quando Há Reserva Ativa
- **Given** que uma baia possui uma reserva com status `PENDENTE_CHECKIN` ou `CHECKED_IN`,
- **When** o gestor tenta excluir a baia,
- **Then** o sistema recusa a exclusão retornando HTTP 400 (`ACTIVE_BOOKINGS_EXIST`) com mensagem explicando que há reservas ativas no espaço.

### Scenario 3: Bloqueio de Permissão para Usuário Não-Gestor
- **Given** um usuário com papel `colaborador`,
- **When** ele tenta enviar uma requisição `DELETE /api/v1/desks/{id}`,
- **Then** a requisição é rejeitada com HTTP 403 Forbidden.

### Scenario 4: Ação de Exclusão com Confirmação no Painel do Gestor
- **Given** que o gestor visualiza a tabela de baias em `AdminDesksView.vue`,
- **When** ele clica no botão "Remover / Excluir" de uma baia,
- **Then** um diálogo de confirmação é exibido solicitando confirmação explícita antes de efetivar a remoção.
