# Specification: Hierarquia Corporativa Completa (Empresas, Prédios, Andares e Baias com CRUDs Completos)

## 1. Feature Overview
Provê uma estrutura corporativa robusta e escalável com suporte a múltiplas empresas, edifícios por empresa, pavimentos por edifício e baias/salas por pavimento, acompanhada de operações completas de criação, leitura, atualização e exclusão (CRUD).

## 2. Acceptance Criteria (BDD)

### Scenario 1: CRUD Completo de Prédios / Edifícios
- **Given** um gestor autenticado,
- **When** ele cria um prédio informando nome, endereço, cidade e total de andares via `POST /api/v1/buildings`,
- **Then** o prédio é persistido, pode ser consultado (`GET /api/v1/buildings`), atualizado (`PUT /api/v1/buildings/{id}`) e excluído (`DELETE /api/v1/buildings/{id}`) se não contiver andares com baias ativas.

### Scenario 2: CRUD Completo de Andares / Pavimentos (Zones)
- **Given** um edifício cadastrado no sistema,
- **When** o gestor cadastra ou edita um pavimento via `POST /api/v1/zones` ou `PUT /api/v1/zones/{id}`,
- **Then** as alterações de nome, andar, descrição e status ativo são salvas; e a exclusão `DELETE /api/v1/zones/{id}` é bloqueada caso existam baias associadas.

### Scenario 3: Atualização de Baias e Salas Existentes
- **Given** uma baia ou sala já cadastrada,
- **When** o gestor envia `PUT /api/v1/desks/{id}` alterando código, equipamentos, tipo de espaço, capacidade ou políticas de tempo/acesso,
- **Then** as alterações são validadas e atualizadas no banco de dados.

### Scenario 4: Gestão Visual por Abas no Painel do Gestor
- **Given** o painel administrativo (`AdminDesksView.vue`),
- **When** o gestor navega pelas abas "Prédios & Sedes", "Pavimentos & Andares" e "Baias & Salas",
- **Then** ele visualiza tabelas completas com botões de ação para Criar, Editar e Excluir para cada entidade, além de poder filtrar a planta 2D e 3D por prédio e andar selecionados.
