# Plan: 3D Avatars, Occupant Visibility, Dedicated Auth UI & QR Code Export

## 1. Problem Statement & Motivation
O usuário apontou quatro deficiências essenciais na experiência do sistema:
1. **Quem reservou não aparece**: As baias ocupadas/reservadas precisam exibir claramente o nome e cargo de quem reservou, tanto no mapa 3D quanto nos modais e listas.
2. **Avatar não visível na baia**: O mapa 3D precisa de marcadores e avatares 3D destacados, com imagem real e nome legível de qualquer ângulo.
3. **Falha na exportação do QR Code**: O link de download do QR Code precisa de autenticação via token Bearer e trigger de download nativo de arquivo PNG com modal de impressão.
4. **Ausência de tela de login e perfil**: Falta uma tela dedicada de Login, Registro com seleção de Avatar e Gerenciamento de Perfil.

## 2. Scope & Boundaries
- **In Scope**:
  - Seed automático no backend de reservas ativas com avatares e nomes para visualização imediata no primeiro carregamento.
  - Ajuste no endpoint `/api/v1/bookings/3d-office` para retornar todos os ocupantes ativos e reservados.
  - Implementação de cartões 3D holográficos com avatar e nome dos ocupantes sobre as baias no Three.js.
  - Tooltip de hover em tempo real no mapa 3D revelando o ocupante da baia.
  - Download nativo autenticado de QR Code PNG e modal de impressão física de adesivos de mesa.
  - Tela completa de Autenticação (`AuthView.vue`) com Login, Registro com seletor de avatar e Meu Perfil.
- **Out of Scope**:
  - Integração com LDAP / Active Directory corporativo externo.

## 3. High-Level Approach
- Refatorar a renderização do avatar em `office3d.ts` para criar texturas de alta definição com foto e nome do ocupante.
- Pre-popular dados no `init_db.py` com reservas ativas demonstrativas.
- Adicionar método de download Blob em `api.ts` e modal de QR Code em `AdminDesksView.vue`.
- Criar a view de autenticação no frontend e integrá-la à navegação principal.

## 4. Dependencies & Prerequisites
- Backend FastAPI e Frontend Vue 3 já existentes.

## 5. Architectural Decision Records (ADRs)
- `.specs/project/ADRs/0001-stack-and-architecture.md`
