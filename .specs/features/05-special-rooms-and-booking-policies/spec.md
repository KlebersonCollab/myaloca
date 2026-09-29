# Specification: Salas de Reunião Especiais, Restrições de Perfil e Políticas de Tempo de Reserva

## 1. Feature Overview
Permite criar e gerenciar salas especiais de reunião e cabines acústicas com controle de acesso por papel de usuário (livre vs restrito a gestores) e limitação de tempo de reserva (ex: no máximo 30 min, 1h, 2h).

## 2. Acceptance Criteria (BDD)

### Scenario 1: Reserva de Sala com Limite de Duração Excedido
- **Given** que uma sala de reunião possui `max_duration_minutes = 60` (máximo 1 hora),
- **When** um colaborador tenta agendar a sala com um intervalo de 2 horas (ex: 14:00 às 16:00),
- **Then** a requisição é rejeitada com erro HTTP 400 (`MAX_DURATION_EXCEEDED`) informando o limite máximo configurado.

### Scenario 2: Reserva de Sala Restrita a Gestores por Colaborador Comum
- **Given** que uma sala executiva possui `required_role = "gestor"`,
- **When** um colaborador com perfil comum tenta realizar a reserva,
- **Then** a requisição é bloqueada com erro HTTP 403 (`RESERVATION_RESTRICTED_ROLE`) e a interface desabilita o botão com aviso de permissão.

### Scenario 3: Reserva Bem-Sucedida por Usuário Autorizado Dentro da Janela Permitida
- **Given** que uma sala de reunião de 1h de duração é solicitada por um gestor para uma reunião de 45 minutos,
- **When** o gestor submete a reserva,
- **Then** a reserva é confirmada com status `PENDENTE_CHECKIN` e o QR Code físico correspondente valida o check-in presencial.

### Scenario 4: Configuração de Políticas pelo Gestor no Painel
- **Given** que o gestor acessa o painel de administração de baias e salas,
- **When** ele seleciona o tipo "Sala de Reunião", define a capacidade (ex: 8 pessoas), marca restrição para "Gestores" e limite de "1 hora",
- **Then** a sala é criada com as políticas persistidas e refletidas no agendamento e mapa 3D.
