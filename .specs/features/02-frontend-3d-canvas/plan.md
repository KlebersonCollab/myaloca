# Plan: Frontend Vue 3 + 3D Office Canvas & Hot-Desking Experience

## 1. Problem Statement & Motivation
O agendamento de baias em planilhas ou listas 2D tradicionais é frio e descontextualizado: o colaborador não sabe ao lado de quem estará sentado nem a iluminação ou layout físico do andar.
O **MyAloca 3D Frontend** traz uma experiência visual imersiva e responsiva em **Vue 3 + Vite + Three.js / TresJS**, permitindo ao colaborador navegar pelo escritório em 3D, ver fotos e avatares dos colegas ocupando as baias em tempo real, reservar assentos com 1 clique e realizar check-in presencial com scanner de QR Code.

## 2. Scope & Boundaries
- **In Scope**:
  - Inicialização da SPA Vue 3 + Vite + TypeScript + Tailwind CSS estruturada estritamente com os tokens Linear Dark de `DESIGN.md`.
  - Integração de cliente HTTP assíncrono com a API FastAPI (`http://localhost:8000/api/v1`).
  - Módulo de Autenticação (Login, Registro, chaveamento entre perfil Gestor e Colaborador).
  - Canvas 3D Interativo do Escritório (Three.js / OrbitControls):
    - Renderização tridimensional de bancadas, monitores duplos e cadeiras em suas posições `(x, y, z)`.
    - Destaque cromático por status (Verde = Livre, Âmbar = Reservado, Roxo = Ocupado).
    - Exibição de avatares e fotos de perfil dos colaboradores sobre as mesas ocupadas.
    - Raycasting interativo para seleção de baias no espaço 3D.
  - Modal/Drawer de Agendamento por horário flexível com detecção de conflitos.
  - Scanner/Leitor de QR Code para confirmação presencial de presença física.
  - Painel do Gestor para visualização das baias e download/impressão dos QR Codes imutáveis.
- **Out of Scope**:
  - Modelagem CAD avançada de prédios inteiros de centenas de andares (foco no andar/zona selecionada).

## 3. High-Level Approach
- Criar a pasta `frontend/` com Vite, Vue 3, TypeScript e Tailwind CSS.
- Encapsular a cena WebGL 3D em um componente reutilizável `OfficeCanvas3D.vue`, mantendo a reatividade do Vue e permitindo controles de câmera fluidos.
- Utilizar a paleta Linear Dark (`#010102`, `#0f1011`, `#5e6ad2`, `#f7f8f8`) de `DESIGN.md` para uma estética refinada e moderna.

## 4. Dependencies & Prerequisites
- Node.js v20+ / v24+ e npm.
- Backend FastAPI ativo em `http://localhost:8000`.

## 5. Architectural Decision Records (ADRs)
- `.specs/project/ADRs/0001-stack-and-architecture.md`: Define o frontend SPA em Vue 3 + Vite + TypeScript + TresJS / Three.js.
