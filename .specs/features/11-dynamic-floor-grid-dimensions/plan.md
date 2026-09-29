# Feature Plan: Planta Dinâmica, Edição de Equipamentos e Drag & Drop de Baias

## 1. Visão Geral
Esta funcionalidade unifica o controle total do layout espacial e dos equipamentos de escritório pelo gestor de facilities. Inclui:
1. Particionamento flexível de colunas e linhas da planta por pavimento (`grid_cols`, `grid_rows`).
2. Semente corporativa completa e idempotente (`init_db.py`).
3. Edição granular de equipamentos por estação (0, 1, 2 monitores, docking station, standing desk, periféricos extras) com reflexo na renderização Three.js.
4. Reposicionamento via Drag & Drop na planta 2D (`AdminDesksView.vue`) e diretamente no cenário 3D (`OfficeCanvas3D.vue`).
5. Edição direta de baias e equipamentos tanto na gestão quanto no modal do mapa 3D (`BookingModal.vue`).

## 2. Escopo da Solução

### 2.1 Backend
- **Modelos e Schemas (`desk.py`)**:
  - `Zone`: `grid_cols` e `grid_rows`.
  - `Desk`: `monitors_count: int` (padrão 1, range 0..4) e `extra_equipment: str | None`.
  - Schemas `DeskBase`, `DeskCreate`, `DeskUpdate`, `DeskResponse`.
  - Manter coerência: se `monitors_count > 0`, `has_monitor = True`; se `0`, `False`.
- **Serviço e Endpoints**:
  - Atualização dos endpoints de `desks` e `zones`.
  - Testes automatizados cobrindo persistência de `monitors_count` e movimentação de coordenadas `pos_x`, `pos_z`.

### 2.2 Frontend
- **Tipagem (`frontend/src/types/index.ts`)**:
  - `Zone`: `grid_cols: number`, `grid_rows: number`.
  - `Desk`: `monitors_count: number`, `extra_equipment?: string | null`.
- **Three.js Visuals (`frontend/src/utils/office3d.ts`)**:
  - Renderizar 0, 1 ou 2 monitores de acordo com `desk.monitors_count`.
- **Painel de Gestão (`frontend/src/views/AdminDesksView.vue`)**:
  - Matriz flexível de colunas e linhas por andar com ajuste rápido.
  - HTML5 Drag and Drop na planta 2D para reposicionar baias soltando em células vazias.
  - Edição de equipamentos no modal da baia (seletor de 0, 1, 2 monitores, docking station, etc.).
- **Maquete 3D Interativa (`frontend/src/components/OfficeCanvas3D.vue` e `BookingModal.vue`)**:
  - Alternador de "Modo Mover (Drag & Drop)" para gestor arrastar baias diretamente pelo chão 3D com snapping e salvar posição.
  - Edição de equipamentos e configurações da baia diretamente dentro de `BookingModal.vue`.

## 3. Riscos e Mitigações
- **Conflito de Interação no 3D**: Durante o arraste de uma baia no mapa 3D, os `OrbitControls` devem ser pausados para evitar que a câmera gire simultaneamente.
- **Snapping e Colisão**: Aplicar step de arredondamento no 3D e evitar sobreposição inadvertida na planta 2D.
