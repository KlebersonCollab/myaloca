# ADR 0010: Edição Granular de Equipamentos e Reposicionamento Drag-and-Drop de Baias no Mapa e na Gestão

## Status
Accepted

## Data
2026-09-28

## Contexto
O gestor de facilities necessita de flexibilidade tanto na configuração física das estações quanto no layout espacial:
1. **Equipamentos das Baias**: Anteriormente, havia apenas uma flag booleana `has_monitor`. O usuário solicita parametrização granular do número de monitores (ex: sem monitor, 1 monitor, 2 monitores) e demais periféricos, com reflexo visual na maquete 3D.
2. **Reposicionamento Espacial Ágil (Drag and Drop)**: Coordenadas numéricas manuais são contraproducentes. O gestor precisa mover baias de forma intuitiva:
   - Na planta da tela de Gestão (`AdminDesksView.vue`): arrastando e soltando baias entre as células da grade 2D.
   - Diretamente no Mapa 3D (`OfficeCanvas3D.vue`): arrastando o objeto 3D sobre o chão do escritório ("Drag & Drop no cenário 3D") com snap à grade e salvamento automático.
3. **Edição Unificada**: A edição de equipamentos e dados da baia deve estar disponível tanto no painel de administração quanto diretamente na maquete 3D ao inspecionar a estação (`BookingModal.vue`).

## Decisão Arquitetural

1. **Modelo e Schemas de Equipamentos**:
   - Adicionar atributo `monitors_count` (inteiro, padrão 1, valores permitidos 0, 1, 2, 3...) na entidade `Desk` (`backend/app/models/desk.py`) e nos schemas `DeskBase`, `DeskCreate`, `DeskUpdate` e `DeskResponse`.
   - Manter sincronização: se `monitors_count > 0`, `has_monitor = True`; se `0`, `False`.
   - Adicionar campo opcional `extra_equipment` (string) para periféricos adicionais (ex: "Headset ANC", "Câmera 4K").

2. **Renderização 3D Condicional no Three.js (`office3d.ts`)**:
   - Se `monitors_count === 0`: nenhum monitor renderizado sobre a mesa.
   - Se `monitors_count === 1`: renderiza 1 monitor centralizado (`x = 0`, `rotY = 0`).
   - Se `monitors_count >= 2`: renderiza monitores duplos angulados (`x = -0.35` e `+0.35`).

3. **Drag and Drop na Planta 2D de Gestão (`AdminDesksView.vue`)**:
   - Células da matriz com baia utilizam a API nativa HTML5 Drag and Drop (`draggable="true"`).
   - Ao soltar a baia em uma célula vazia (`@drop`), calcula as coordenadas `pos_x` e `pos_z` correspondentes e executa `api.desks.update(deskId, { pos_x, pos_z })`.

4. **Modo Drag & Drop no Mapa 3D (`OfficeCanvas3D.vue`)**:
   - Controle alternável para gestores/administradores: **"Modo Mover Baias (Drag & Drop)"**.
   - Quando ativo:
     - Os controles de órbita da câmera (`OrbitControls`) são temporariamente suspensos durante o arraste.
     - Raycasting no plano do chão (`THREE.Plane(0, 1, 0)`) calcula a posição do cursor em tempo real.
     - Aplica *grid snapping* (passo de 1.2m) e atualiza a posição visual da baia.
     - No evento `mouseup`, dispara `api.desks.update(desk.id, { pos_x, pos_z })` persistindo as novas coordenadas imediatamente.

5. **Edição Direta pelo Mapa 3D (`BookingModal.vue`)**:
   - Ao clicar em qualquer baia no mapa 3D, usuários com papel `admin` ou `gestor` visualizam a aba ou botão **"Editar Equipamentos & Baia"**.
   - Permite alterar quantidade de monitores (0, 1, 2), docking station, standing desk e código diretamente sem sair da maquete 3D.

## Consequências
- **Positivas**:
  - Máxima ergonomia operacional para o gestor configurar o layout do escritório física e virtualmente.
  - Fidelidade visual 3D em relação ao setup de equipamentos real de cada estação.
  - Sincronização bidirecional completa entre a planta 2D, o mapa 3D e o banco de dados.
