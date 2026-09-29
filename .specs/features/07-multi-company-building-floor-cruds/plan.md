# Plan: Hierarquia Corporativa Completa (Empresas, Prédios, Andares e Baias com CRUDs Completos)

## 1. Problem Statement & Motivation
O modelo anterior tratava pavimentos e baias de forma isolada, sem suportar empresas com múltiplos prédios ou operações com filiais. Além disso, as operações administrativas careciam de CRUDs completos (edição e exclusão de andares/setores, prédios e baias). É fundamental estruturar a hierarquia corporativa `Company -> Building -> Floor/Zone -> Desk/Space` e disponibilizar CRUDs completos com filtros e gestão visual.

## 2. Scope & Boundaries
- **In Scope**:
  - Modelos SQLAlchemy & Pydantic: `Company`, `Building`, evolução de `Zone` com `building_id`, e schemas de Create/Update/Response.
  - Endpoints RESTful completos:
    - `/api/v1/companies` (GET, POST, PUT, DELETE)
    - `/api/v1/buildings` (GET, POST, PUT, DELETE)
    - `/api/v1/zones` (GET, POST, PUT, DELETE com verificação de baias vinculadas)
    - `/api/v1/desks` (adição de PUT para edição completa de baias)
  - Seeds iniciais: Empresa matriz ("TechCorp Brasil"), Edifício Principal ("Sede Faria Lima - SP") e Edifício Secundário ("Hub Sul - Curitiba").
  - Testes automatizados cobrindo todos os novos CRUDs e validações.
  - Frontend: Atualização de `types/index.ts` e `services/api.ts`.
  - Frontend: Hub de Administração de Facilities (`AdminDesksView.vue`) com abas para:
    - Gerenciar Prédios (Listar, Criar, Editar, Excluir)
    - Gerenciar Andares/Setores (Listar, Criar, Editar, Excluir)
    - Gerenciar Baias/Salas (Listar, Criar, Editar, Excluir, Assistente, Planta)
    - Seletor de Prédio e Andar integrado.
- **Out of Scope**:
  - Faturamento multi-moeda entre filiais internacionais.

## 3. High-Level Approach
1. Criar modelos `Company` e `Building`, associar a `Zone` de forma retrocompatível.
2. Criar serviços e endpoints com validação de chaves estrangeiras e integridade referencial.
3. Criar suíte de testes completa em `test_buildings.py` e expandir `test_desks.py`.
4. Atualizar interfaces e cliente API no frontend, montando as abas e modais de edição/exclusão.

## 4. Dependencies & Prerequisites
- SQLAlchemy 2.0 Async, Pydantic v2, FastAPI, Vue 3.

## 5. Architectural Decision Records (ADRs)
- ADR 0005: Hierarquia Multi-Empresa, Multi-Prédio, Andares e CRUDs Completos
