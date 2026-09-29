# ADR 0003: Espaços Especiais (Salas de Reunião & Cabines Focus) e Políticas de Reserva

## Status
Accepted

## Contexto
Em ambientes corporativos híbridos modernos, escritórios não possuem apenas baias individuais de trabalho, mas também salas de reunião, salas de diretoria e cabines acústicas individuais (Phone Booths / Focus). O agendamento desses espaços possui regras específicas:
1. **Controle de Acesso por Perfil**: Algumas salas podem ser de uso livre para qualquer colaborador, enquanto outras são restritas a gestores/liderança (ex: Sala de Reunião da Diretoria).
2. **Políticas de Tempo / Limite de Duração**: Para evitar que salas de reunião sejam monopolizadas o dia todo por um único grupo, deve ser possível limitar a duração máxima de cada reserva (ex: no máximo 30 minutos, 1 hora, 2 horas ou livre).
3. **Capacidade**: Salas acomodam múltiplos ocupantes (ex: 4 a 12 pessoas).
4. **Governança no Painel Administrativo**: O gestor deve ser capaz de definir e alterar essas propriedades diretamente no painel de facilities.

## Decisão
1. **Extensão da Entidade Desk (Espaço de Trabalho)**:
   - Adicionar atributos ao modelo `Desk`:
     - `space_type: str`: `"BAIA"`, `"SALA_REUNIAO"`, `"CABINE_FOCUS"`.
     - `capacity: int`: capacidade de pessoas (padrão 1 para baia, 4 a 12 para reuniões).
     - `required_role: str | None`: `None` (acesso livre) ou `"gestor"`/`"admin"` (restrito a liderança).
     - `max_duration_minutes: int | None`: `None`/`0` (sem limite) ou limite em minutos (`30`, `60`, `120`, `240`).
2. **Motor de Validação de Políticas no Backend**:
   - Em `BookingService.create_booking`:
     - Se `desk.required_role` for exigido, validar se o usuário solicitante possui a permissão adequada. Caso contrário, rejeitar com `403 Forbidden` (`RESERVATION_RESTRICTED_ROLE`).
     - Se `desk.max_duration_minutes` estiver ativo, calcular `(end_time - start_time)` e rejeitar se exceder o teto com `400 Bad Request` (`MAX_DURATION_EXCEEDED`).
3. **Interface de Reserva Inteligente**:
   - `BookingModal.vue` exibe badges informativos sobre o tipo de espaço, capacidade, limites de tempo e restrições de perfil.
   - Ajusta os horários sugeridos de acordo com a política e desativa a confirmação se o colaborador não tiver o perfil necessário.
4. **Configuração de Facilidades no Painel do Gestor**:
   - O `AdminDesksView.vue` permite configurar o tipo do espaço, a restrição de perfil e a duração máxima tanto no assistente de criação quanto na visualização tabular.

## Consequências
- **Positivas**:
  - Elimina conflitos e monopolização de salas de reunião.
  - Oferece governança corporativa realista de facilities.
  - Mantém 100% de retrocompatibilidade com baias já cadastradas.
