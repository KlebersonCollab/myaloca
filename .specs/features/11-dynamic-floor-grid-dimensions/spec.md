# Feature Specification: Planta Dinâmica, Edição de Equipamentos e Drag & Drop de Baias

## 1. User Stories
- **US-1 (Gestor/Facilities)**: Como gestor, quero editar os equipamentos de cada baia (definir 1 monitor, 2 monitores, docking station, etc.) tanto no painel de administração quanto clicando na baia no mapa 3D, para manter o inventário fiel à realidade.
- **US-2 (Gestor/Facilities)**: Como gestor, quero poder mover uma baia de lugar via drag and drop na grade da planta e também arrastando-a diretamente no cenário 3D, para organizar o layout com velocidade e ergonomia.
- **US-3 (Gestor/Facilities)**: Como gestor, quero definir livremente quantas colunas e linhas a grade da planta possui por andar, permitindo particionamentos variados (ex: 8 colunas por linha ou 10x5).

## 2. Business Rules & Invariants
- **BR-1 (Equipment Definition)**: O atributo `monitors_count` aceita valores `>= 0`. Caso `monitors_count >= 1`, a flag `has_monitor` é automaticamente ativada como `True`; se `0`, `has_monitor` é `False`.
- **BR-2 (Visual 3D Monitor Fidelity)**:
  - `monitors_count === 0`: Nenhum monitor renderizado na mesa 3D.
  - `monitors_count === 1`: Exatamente 1 monitor renderizado centralizado (`x = 0`).
  - `monitors_count >= 2`: 2 monitores renderizados em ângulo estéreo.
- **BR-3 (Drag and Drop Persistence)**:
  - Ao soltar a baia em nova célula 2D ou posição 3D, uma requisição `PUT /api/v1/desks/{id}` é disparada atualizando `pos_x` e `pos_z`.
  - No 3D, a movimentação deve aplicar grid snapping (passo de 1.2m) e desativar `OrbitControls` durante a ação de arraste.
- **BR-4 (Dynamic Grid Sizing)**: O número de colunas e linhas da `Zone` pode ser ajustado a qualquer momento e persiste via `PUT /api/v1/zones/{id}`.

## 3. Acceptance Criteria

### Cenário 1: Edição de Equipamentos das Baias
- **AC-1 (Edição de Monitores e Periféricos no Backend)**:
  - *Given* uma baia existente,
  - *When* o gestor enviar `PUT /api/v1/desks/{id}` com `monitors_count=2` e `has_docking_station=True`,
  - *Then* o registro é atualizado e retornado com `monitors_count=2`, `has_monitor=True` e HTTP 200.
- **AC-2 (Reflexo Visual no Three.js)**:
  - *Given* uma baia com `monitors_count=1`,
  - *When* o mapa 3D for renderizado,
  - *Then* é instanciada apenas uma tela centralizada na bancada 3D.

### Cenário 2: Drag & Drop na Planta 2D (Admin)
- **AC-3 (Arrastar e Soltar na Grade)**:
  - *Given* a planta interativa em `AdminDesksView.vue`,
  - *When* o gestor arrastar o card de uma baia e soltar sobre uma célula vazia da matriz,
  - *Then* as coordenadas `pos_x` e `pos_z` são recalculadas e salvas no backend, e a baia passa a ocupar a nova célula.

### Cenário 3: Drag & Drop no Mapa 3D
- **AC-4 (Modo Mover no Three.js)**:
  - *Given* o mapa 3D com o botão "Modo Mover (Drag & Drop)" ativado pelo gestor,
  - *When* o gestor clicar e arrastar uma baia pelo chão do escritório e soltá-la,
  - *Then* o objeto 3D se move acompanhando o cursor com grid snap e as coordenadas atualizadas são persistidas via API.

### Cenário 4: Edição de Baia Direto no Mapa 3D
- **AC-5 (Modal de Edição no Mapa 3D)**:
  - *Given* o mapa 3D,
  - *When* o gestor clicar em qualquer baia e acionar "Editar Baia",
  - *Then* abre-se o formulário de edição de equipamentos e dados da baia diretamente na tela 3D.

## 4. Test Data Matrix
| Caso de Teste | Operação | Dados | Resultado Esperado |
|---|---|---|---|
| Baia com 1 monitor | `PUT /desks/{id}` | `monitors_count=1` | 200 OK, `has_monitor=True` |
| Baia com 0 monitores | `PUT /desks/{id}` | `monitors_count=0` | 200 OK, `has_monitor=False` |
| Mover baia coordenadas | `PUT /desks/{id}` | `pos_x=4.8`, `pos_z=-1.2` | 200 OK, coordenadas persistidas |
