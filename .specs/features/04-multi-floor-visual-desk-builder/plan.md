# Plan: Suporte a Prédios Multi-Andares e Construtor Visual de Baias Sem Coordenadas Manuais

## 1. Problem Statement & Motivation
Atualmente, o cadastro de baias exige que o gestor forneça valores numéricos cartesianos `(pos_x, pos_y, pos_z)`, gerando complexidade indevida e frustração para usuários não-técnicos. Além disso, edifícios corporativos modernos contam com múltiplos andares (N andares) e setores distribuídos. É indispensável prover:
- Gestão de múltiplos andares corporativos com alternância rápida na visualização 3D.
- Assistente amigável de criação de baias por fileiras/bancadas e grade visual interativa sem digitação de números de coordenadas.

## 2. Scope & Boundaries
- **In Scope**:
  - Backend: Filtragem por `floor` em `/api/v1/zones`, `/api/v1/desks` e `/api/v1/bookings/3d-office`.
  - Backend: Endpoint para criação em lote de baias (`/api/v1/desks/batch`) ou cálculo de layout no serviço.
  - Backend: Seed de banco com múltiplos andares corporativos (Andar 1 - Open Space, Andar 2 - Engenharia, Andar 3 - Diretoria).
  - Frontend: Seletor de Andares corporativo no mapa 3D (`OfficeCanvas3D.vue`) com navegação entre pavimentos.
  - Frontend: Assistente inteligente de Bancadas e Fileiras em `AdminDesksView.vue` que calcula posições e rotações automaticamente.
  - Frontend: Grade Visual 2D (Mini-Planta Baixa) para posicionamento com clique direto na célula ("Click-to-Place").
  - Frontend: Modal rápido para cadastrar novos andares e setores no edifício.
- **Out of Scope**:
  - Modelagem CAD/BIM de paredes estruturais complexas ou elevadores 3D dinâmicos.

## 3. High-Level Approach
1. Estender `DeskService` e endpoints para suporte a filtro de piso e criação em lote/assistida de baias.
2. Em `OfficeCanvas3D.vue`, incluir seletor de Andar destacado (ex: tabs ou pílulas dos andares do prédio) que recarrega a cena 3D com as baias daquele piso específico.
3. Em `AdminDesksView.vue`, substituir o formulário de coordenadas numéricas por um Assistente de Bancadas com preview visual e grade de alocação por clique.
4. Adicionar modal para "+ Novo Andar / Setor".

## 4. Dependencies & Prerequisites
- SQLAlchemy 2.0 Async, FastAPI, Vue 3, Three.js, Lucide Icons.

## 5. Architectural Decision Records (ADRs)
- ADR 0001: Seleção de Stack Tecnológica e Arquitetura do MyAloca
- ADR 0002: Suporte a Edifícios Multi-Andares e Construtor Visual de Baias Sem Coordenadas Manuais
