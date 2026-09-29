# Feature Specification: CRUD de Departamentos e Liberação Antecipada de Reservas

## 1. User Stories
- **US-1 (Gestor/Admin)**: Como administrador ou gestor, quero cadastrar, listar, editar e excluir departamentos corporativos (com nome, sigla e descrição), para estruturar a organização e padronizar o perfil dos colaboradores.
- **US-2 (Colaborador)**: Como colaborador, quero selecionar meu departamento a partir de uma lista padronizada no meu perfil, para manter meus dados cadastrais consistentes.
- **US-3 (Colaborador)**: Como colaborador que reservou uma baia mas não irá mais usá-la, quero cancelar minha reserva pendente, liberando o assento para outro colega.
- **US-4 (Colaborador)**: Como colaborador que fez check-in e precisa ir embora do escritório mais cedo, quero poder encerrar/liberar minha reserva com um clique, para que a baia fique imediatamente disponível para outra pessoa trabalhar no restante do dia.

## 2. Business Rules & Invariants
- **BR-1 (Department Uniqueness)**: O nome e a sigla do departamento devem ser únicos dentro da mesma empresa.
- **BR-2 (Department Deletion Guard)**: Um departamento com colaboradores ativos associados NÃO pode ser excluído (`DEPARTMENT_HAS_USERS`). O gestor deve primeiro remanejar os colaboradores.
- **BR-3 (Early Checkout Window Shrinking)**: Ao realizar a liberação antecipada de uma reserva com presença confirmada (`CHECKED_IN`), o `end_time` da reserva é truncado para a hora atual (`now`), e o status é definido como `FINALIZADA` (ou `CANCELADA_USUARIO`), liberando imediatamente a baia (`desk.status = "DISPONIVEL"`).
- **BR-4 (Overlap Resolution)**: Após o cancelamento ou liberação antecipada, novas tentativas de reserva para a mesma baia no intervalo de horário liberado não devem gerar conflito (`BOOKING_OVERLAP`).
- **BR-5 (Booking Ownership Guard)**: Apenas o próprio usuário titular da reserva ou um administrador/gestor tem permissão para cancelar ou liberar uma reserva.

## 3. Acceptance Criteria

### Cenário 1: CRUD de Departamentos
- **AC-1 (Criação de Departamento)**:
  - *Given* um usuário autenticado com perfil `admin` ou `gestor`,
  - *When* enviar `POST /api/v1/departments` com `name="Engenharia de Software"`, `code="ENG"`,
  - *Then* o departamento é persistido com sucesso e retorna HTTP 201 com id e timestamps.
- **AC-2 (Listagem e Filtros de Departamentos)**:
  - *Given* departamentos existentes no banco,
  - *When* enviar `GET /api/v1/departments`,
  - *Then* retorna a lista de departamentos com a contagem de colaboradores alocados em cada um.
- **AC-3 (Proteção na Exclusão de Departamento com Membros)**:
  - *Given* um departamento com colaboradores vinculados,
  - *When* enviar `DELETE /api/v1/departments/{id}`,
  - *Then* o sistema retorna HTTP 400 com código `DEPARTMENT_HAS_USERS` e impede a exclusão.

### Cenário 2: Cancelamento de Reserva Pendente
- **AC-4 (Cancelamento de Reserva Pendente)**:
  - *Given* uma reserva com status `PENDENTE_CHECKIN`,
  - *When* o titular da reserva clicar em "Cancelar Reserva" ou enviar `POST /api/v1/bookings/{id}/cancel`,
  - *Then* o status da reserva é alterado para `CANCELADA_USUARIO` e a baia volta para `DISPONIVEL`.

### Cenário 3: Liberação Antecipada de Reserva Confirmada (Early Checkout)
- **AC-5 (Liberação Antecipada de Reserva com Check-in Realizado)**:
  - *Given* uma reserva confirmada (`CHECKED_IN`) com término agendado para 18:00,
  - *When* o usuário decide sair às 14:00 e aciona "Liberar Baia / Saída Antecipada",
  - *Then* o `end_time` da reserva é atualizado para 14:00 (hora do checkout), o status muda para `FINALIZADA`, a baia é definida como `DISPONIVEL` e o avatar 3D é desocupado da estação.
- **AC-6 (Reagendamento Imediato da Baia Desocupada)**:
  - *Given* uma baia liberada antecipadamente às 14:00 que originalmente estava reservada até 18:00,
  - *When* outro colaborador tenta reservar essa mesma baia das 14:30 às 18:00,
  - *Then* a reserva é criada com sucesso sem erro de sobreposição (`BOOKING_OVERLAP`).

## 4. Test Data Matrix
| Caso de Teste | Endpoint | Payload / Condição | Resultado Esperado |
|---|---|---|---|
| Criar departamento válido | `POST /departments` | `{"name": "Design", "code": "DSG"}` | 201 Created |
| Listar departamentos | `GET /departments` | Sem filtros | 200 OK com lista |
| Bloquear exclusão com usuários | `DELETE /departments/{id}` | Usuário associado ao dept | 400 `DEPARTMENT_HAS_USERS` |
| Cancelar reserva pendente | `POST /bookings/{id}/cancel` | `PENDENTE_CHECKIN` | 200 `CANCELADA_USUARIO` |
| Liberar antecipado checked-in | `POST /bookings/{id}/checkout` | `CHECKED_IN`, `end_time > now` | 200 `FINALIZADA`, `end_time = now` |
| Reservar janela liberada | `POST /bookings` | Horário antes ocupado | 201 Created |
