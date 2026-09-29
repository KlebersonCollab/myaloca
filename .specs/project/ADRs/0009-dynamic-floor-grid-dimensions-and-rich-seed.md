# ADR 0009: Dimensões Dinâmicas da Grade do Pavimento e Seed Corporativa Completa

## Status
Accepted

## Data
2026-09-28

## Contexto
Anteriormente, a planta interativa de alocação de baias no painel de administração (`AdminDesksView.vue`) possuía uma matriz rígida fixa de 6 colunas por 4 linhas (6x4 = 24 posições). No mundo real de facilities, cada pavimento ou andar de um edifício possui layout, proporções e capacidade distintas (por exemplo, 8x4, 10x5, 12x4 ou salas menores com 4x3).
Além disso, a base inicial de semente de dados (`init_db.py`) ainda não contemplava a hierarquia completa desenvolvida nas últimas iterações (`Company`, `Building`, `Department`, vinculação com usuários e metadados de grade nos pavimentos).

## Decisão Arquitetural

1. **Extensão do Modelo `Zone` com Metadados de Grade**:
   - Adicionar atributos `grid_cols` (padrão 6, min 2) e `grid_rows` (padrão 4, min 2) na entidade `Zone` (`backend/app/models/desk.py`).
   - Expor os campos em `ZoneBase`, `ZoneCreate`, `ZoneUpdate` e `ZoneResponse` (`backend/app/schemas/desk.py`).
   - Garantir que o endpoint `PUT /api/v1/zones/{id}` permita atualização imediata das dimensões da grade.

2. **Planta Interativa Flexível e Parametrizável pelo Gestor (`AdminDesksView.vue`)**:
   - O gestor pode definir o particionamento (número de colunas e linhas) tanto no cadastro/edição de pavimentos quanto diretamente na barra da Planta Interativa do Andar (ajuste rápido com botão "Salvar Grade").
   - A grade CSS renderiza dinamicamente via `grid-template-columns: repeat(${activeGridCols}, minmax(105px, 1fr))`, com scroll horizontal automático quando a grade for muito ampla.
   - A fórmula de cálculo de coordenadas espaciais 3D `(posX, posZ)` adapta-se dinamicamente às dimensões ativas do andar:
     - `posX = (colIndex - (grid_cols - 1) / 2) * 2.4`
     - `posZ = (rowIndex - (grid_rows - 1) / 2) * 2.4`
   - A busca e encaixe de baias nas células da grade considera as dimensões e o centro dinâmico do pavimento.

3. **Atualização Completa da Seed de Dados (`backend/app/db/init_db.py`)**:
   - Criação da empresa padrão `Company` ("MyAloca Corporate", código `MYALOCA-HQ`).
   - Criação do edifício sede `Building` ("Torre Paulista Sede", 3 andares).
   - Criação dos departamentos `Department` ("Engenharia", "Design", "Operações", "Analytics").
   - Vinculação dos usuários demo aos seus respectivos departamentos corporativos (`department_id`).
   - Criação dos pavimentos `Zone` vinculados ao edifício, com dimensões variadas para comprovar o particionamento dinâmico:
     - 1º Andar: 6 colunas × 4 linhas (Open Space)
     - 2º Andar: 8 colunas × 4 linhas (Engenharia & Produto - layout amplo com 8 baias por linha)
     - 3º Andar: 6 colunas × 3 linhas (Diretoria & Salas Executivas)
   - Cadastramento das baias, salas de reunião e cabines focus com coordenadas alinhadas às novas grades.

## Consequências
- **Positivas**:
  - Liberdade total para os gestores desenharem plantas de qualquer dimensão ou formato por andar.
  - Dados iniciais (seed) refletem a totalidade das features desenvolvidas (multi-empresa, multi-prédio, departamentos, salas e políticas).
  - A experiência 3D e 2D mantém paridade espacial fiel ao particionamento escolhido pelo gestor.
