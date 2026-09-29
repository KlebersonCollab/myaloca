# Feature Specification: Cancelamento Administrativo e Liberação de Baias

## 1. User Stories
- **US-1 (Administrador/Gestor)**: Como administrador ou gestor, quero liberar ou cancelar a reserva de qualquer baia diretamente no painel de facilities quando o colaborador me avisar que foi embora ou faltou, para que a estação volte a ficar disponível para outros colaboradores imediatamente.
- **US-2 (Administrador/Gestor)**: Como administrador ou gestor navegando pela maquete 3D, quero clicar em qualquer baia ocupada e poder liberá-la através do modal da estação, para agilizar a operação presencial sem ter que navegar até tabelas administrativas.
- **US-3 (Colaborador Comum)**: Como colaborador comum, quero que o sistema me impeça de cancelar reservas de outras pessoas, garantindo a integridade dos assentos de meus colegas.

## 2. Business Rules & Invariants
- **BR-1 (Admin/Gestor Privilege)**: Apenas usuários com papel `admin` ou `gestor` (ou o próprio usuário titular) possuem permissão para executar a liberação administrativa de uma baia.
- **BR-2 (Desk Status Transition)**: Ao executar a liberação, a baia deve transitar imediatamente para `DISPONIVEL` (a menos que esteja em `MANUTENCAO`).
- **BR-3 (Active Booking Shrinking)**: Qualquer reserva associada à baia em status `PENDENTE_CHECKIN` ou `CHECKED_IN` deve ter seu `end_time` truncado para o horário da operação (`now`) e seu status atualizado para `FINALIZADA` (caso check-in realizado) ou `CANCELADA_USUARIO`/`CANCELADA_ADMIN`.
- **BR-4 (Instant 3D Synchronization)**: A liberação deve emitir evento de atualização reativo no frontend para limpar o avatar 3D e o crachá de ocupação da estação no Three.js WebGL.

## 3. Acceptance Criteria

### Cenário 1: Liberação Administrativa no Painel de Baias
- **AC-1 (Liberação de Baia Ocupada por Admin)**:
  - *Given* uma baia com status `OCUPADA` e reserva ativa de um colaborador,
  - *When* o administrador acionar `POST /api/v1/desks/{id}/release` ou clicar em "Liberar" na tabela,
  - *Then* o status da baia passa para `DISPONIVEL`, a reserva ativa é finalizada e a resposta retorna HTTP 200.
- **AC-2 (Bloqueio para Colaborador Comum)**:
  - *Given* um usuário comum (`colaborador`),
  - *When* tentar chamar `POST /api/v1/desks/{id}/release`,
  - *Then* o sistema retorna HTTP 403 Forbidden.

### Cenário 2: Liberação Direta no Modal da Maquete 3D
- **AC-3 (Ação de Gestor no Modal da Baia)**:
  - *Given* um gestor ou admin visualizando a maquete 3D,
  - *When* clicar em uma baia com status `RESERVADA` ou `OCUPADA`,
  - *Then* o modal exibe os dados do ocupante e o botão "Liberar Baia / Cancelar Reserva (Gestor)", permitindo liberar o espaço em 1 clique.

## 4. Test Data Matrix
| Caso de Teste | Endpoint | Papel | Condição | Resultado Esperado |
|---|---|---|---|---|
| Admin libera baia ocupada | `POST /desks/{id}/release` | Admin | Baia com booking ativo | 200 OK, Baia `DISPONIVEL` |
| Gestor libera baia reservada | `POST /desks/{id}/release` | Gestor | Baia com booking pendente | 200 OK, Baia `DISPONIVEL` |
| Colaborador tenta liberar | `POST /desks/{id}/release` | Colaborador | Baia de outro usuário | 403 Forbidden |
| Baia sem reserva ativa | `POST /desks/{id}/release` | Admin | Baia já disponível | 200 OK, status mantido |
