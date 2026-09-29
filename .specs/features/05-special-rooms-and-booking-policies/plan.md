# Plan: Salas de Reunião Especiais, Restrições de Perfil e Políticas de Tempo de Reserva

## 1. Problem Statement & Motivation
Ambientes corporativos demandam tipos variados de espaços além de baias individuais, em especial **Salas de Reunião** e **Cabines Telefônicas/Focus**. Sem políticas de reserva, salas concorridas podem ser monopolizadas o dia inteiro ou agendadas indevidamente por colaboradores sem autorização para salas executivas da diretoria. É necessário permitir configuração granular pelo gestor de tipo de espaço, restrição por perfil e limite de horas por reserva.

## 2. Scope & Boundaries
- **In Scope**:
  - Modelo `Desk` estendido com `space_type` (`BAIA`, `SALA_REUNIAO`, `CABINE_FOCUS`), `capacity`, `required_role`, `max_duration_minutes`.
  - Backend: Validação rigorosa em `create_booking` para tempo máximo e verificação de perfil permitido.
  - Backend: Seeds de salas de reunião no 2º e 3º andares com políticas de 1 hora e restrição a gestores.
  - Frontend: `BookingModal.vue` com exibição de tipo de sala, capacidade, limite de tempo e bloqueio visual para perfis não autorizados.
  - Frontend: `AdminDesksView.vue` com opções no Assistente de Baias para criar Salas de Reunião e configurar políticas de tempo/perfil.
  - Testes automatizados pytest cobrindo rejeição de reserva com tempo excedido e rejeição por perfil não autorizado.
- **Out of Scope**:
  - Integração com sistemas de videoconferência externos (ex: Zoom Room API / Google Meet Hardware).

## 3. High-Level Approach
1. Atualizar colunas SQLAlchemy em `Desk` e schemas Pydantic em `DeskBase`.
2. Adicionar validação de políticas no `BookingService.create_booking` e expor códigos de erro semânticos.
3. Atualizar a UI do modal de reserva e do painel do gestor para permitir configurar e visualizar as restrições com clareza.

## 4. Dependencies & Prerequisites
- SQLAlchemy 2.0 Async, Pydantic v2, FastAPI, Vue 3, Three.js.

## 5. Architectural Decision Records (ADRs)
- ADR 0001: Seleção de Stack Tecnológica e Arquitetura do MyAloca
- ADR 0002: Suporte a Edifícios Multi-Andares e Construtor Visual de Baias Sem Coordenadas Manuais
- ADR 0003: Espaços Especiais (Salas de Reunião & Cabines Focus) e Políticas de Reserva
