# ADR 0004: Governança de Remoção de Baias e Proteção de Reservas Ativas

## Status
Accepted

## Contexto
Durante o ciclo de vida do edifício de escritórios, gestores de facilities precisam reconfigurar layouts, desativar ou remover estações de trabalho e salas especiais. No entanto, uma baia pode conter histórico de reservas passadas ou, criticamente, reservas ativas no presente ou futuro (`PENDENTE_CHECKIN` ou `CHECKED_IN`).
Remover descontroladamente uma baia com pessoas agendadas geraria quebra na integridade operacional dos colaboradores.

## Decisão
1. **Regra de Proteção Ativa (Active Booking Guard)**:
   - Uma baia NÃO pode ser removida se possuir reservas ativas (`status` em `["PENDENTE_CHECKIN", "CHECKED_IN"]`).
   - Caso um gestor tente remover, o backend rejeita com HTTP 400 (`ACTIVE_BOOKINGS_EXIST`).
2. **Limpeza de Histórico Não-Ativo**:
   - Se a baia possuir apenas reservas passadas, canceladas ou finalizadas (`FINALIZADA`, `CANCELADA_USUARIO`, `EXPIRADA_NO_SHOW`), a remoção é permitida e remove os vínculos dependentes antes de deletar a baia.
3. **Endpoint Seguro & Autorização**:
   - `DELETE /api/v1/desks/{id}` restrito exclusivamente a usuários com papel `gestor` ou `admin`.
4. **Interface do Usuário com Confirmação Modal**:
   - O painel administrativo exibe botão de exclusão na tabela e na visualização da baia, com diálogo explícito de confirmação para evitar cliques acidentais.

## Consequências
- **Positivas**:
  - Evita exclusão acidental de estações em uso imediato.
  - Oferece total autonomia para o gestor manter a planta limpa e atualizada.
  - Garante integridade referencial nas tabelas de banco de dados.
