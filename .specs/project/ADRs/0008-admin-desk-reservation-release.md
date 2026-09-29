# ADR 0008: Cancelamento Administrativo e Liberação Direta de Baias Ocupadas

## Status
Accepted

## Data
2026-09-28

## Contexto
Em ambientes de escritório híbrido, é comum que colaboradores queiram liberar sua estação mas não tenham acesso imediato ao celular/aplicativo no momento da saída (ou simplesmente avisem verbalmente ou via chat ao gestor/administrador de facilities que já foram embora).
Anteriormente:
- Apenas o próprio usuário titular da reserva conseguia cancelar via interface ("Minhas Reservas").
- No painel administrativo de baias (`AdminDesksView.vue`) e na maquete 3D (`BookingModal.vue`), gestores e administradores não possuíam botão para forçar a liberação ou cancelamento de uma baia ocupada/reservada por terceiros.
- A baia permanecia bloqueada na tabela, no mapa 3D e no calendário até o final do expediente agendado, gerando ociosidade invisível e impedindo agendamentos legítimos de outros membros.

## Decisão Arquitetural

1. **Endpoint Administrativo de Liberação de Baia (`POST /api/v1/desks/{desk_id}/release`)**:
   - Criação de endpoint restrito a perfis com privilégio (`admin` e `gestor`) em `backend/app/api/v1/endpoints/desks.py`.
   - Localiza qualquer reserva ativa (`PENDENTE_CHECKIN` ou `CHECKED_IN`) associada à baia:
     - Trunca o `end_time` da reserva para `now` (hora da liberação).
     - Altera o status da reserva para `FINALIZADA` (caso tenha havido check-in) ou `CANCELADA_USUARIO` (caso pendente).
     - Altera o status da baia para `DISPONIVEL`.
   - Caso a baia esteja em status `RESERVADA` ou `OCUPADA` sem reserva ativa no momento, redefine o status da baia diretamente para `DISPONIVEL`.
   - Retorna os dados atualizados da baia e da reserva liberada.

2. **Ação Direta no Painel Administrativo de Baias (`AdminDesksView.vue`)**:
   - Na tabela de Baias & Salas, quando uma baia estiver em status `RESERVADA` ou `OCUPADA`, exibir botão em destaque: **"Liberar"** (com ícone `LogOut` ou `Unlock`).
   - Ao clicar, abre modal de confirmação explicando que a reserva atual da baia será encerrada imediatamente e o assento voltará a ficar disponível para agendamento.
   - Chamada a `api.desks.release(deskId)` com recarregamento síncrono.

3. **Ação Administrativa no Modal da Maquete 3D (`BookingModal.vue`)**:
   - Ao abrir o modal de uma baia ocupada (`OCUPADA`) ou reservada (`RESERVADA`) no mapa 3D, se o usuário logado for `admin` ou `gestor` (ou o próprio ocupante), exibir botão administrativo em destaque: **"Liberar Baia Agora (Gestor)"**.
   - Ao confirmar, dispara a liberação da baia, fecha o modal, emite evento de atualização e limpa o avatar 3D da estação na maquete WebGL.

## Consequências
- **Positivas**:
  - Flexibilidade operacional total para os gestores de facilities gerenciarem o fluxo presencial de mesas.
  - Eliminação de assentos "fantasmas" travados por quem já deixou o escritório.
  - Sincronização em tempo real entre a ação administrativa, o banco de dados e a maquete 3D interativa.
- **Negativas / Cuidados**:
  - Exclusivo para administradores e gestores para impedir que colaboradores cancelem reservas alheias indevidamente.
