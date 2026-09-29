# ADR 0005: Hierarquia Multi-Empresa, Multi-Prédio, Andares e CRUDs Completos

## Status
Accepted

## Contexto
Na versão inicial, o modelo de dados suportava apenas Zonas/Andares soltos e Baias vinculadas a uma única zona sem contexto de empresa ou prédio.
Empresas modernas operam em modelos com múltiplas unidades, prédios comerciais ou subsidiárias. O gestor precisa de um modelo hierárquico consistente:
`Empresa (Company) -> Prédio (Building) -> Andar/Setor (Zone) -> Baia/Sala (Desk)`
Além disso, todas essas entidades devem possuir CRUDs completos (Create, Read, Update, Delete) com validação de dependências e interfaces administrativas ricas.

## Decisão
1. **Entidade Company (Empresa / Organização)**:
   - Atributos: `id`, `name`, `code` (slug único), `cnpj`, `is_active`, `created_at`.
   - Relacionamento: 1:N com `Building` e 1:N com `User`.
2. **Entidade Building (Prédio / Edifício Corporativo)**:
   - Atributos: `id`, `company_id` (opcional com default), `name`, `address`, `city`, `total_floors`, `is_active`, `created_at`.
   - Relacionamento: 1:N com `Zone`.
3. **Evolução da Entidade Zone (Andar / Pavimento / Setor)**:
   - Adicionar chave estrangeira `building_id` (opcional com default para retrocompatibilidade).
   - CRUD completo: `GET /zones`, `POST /zones`, `PUT /zones/{id}`, `DELETE /zones/{id}` (com guarda de dependência de baias).
4. **CRUD Completo de Baias / Salas**:
   - Adicionar `PUT /desks/{id}` para permitir edição de código, equipamentos, capacidade, restrição de papel e tempo máximo.
5. **Painel do Gestor Unificado (Hub de Facilities)**:
   - Interface com abas integradas:
     - Gestão de Prédios & Sedes (CRUD)
     - Gestão de Pavimentos & Andares (CRUD)
     - Gestão de Baias & Salas Especiais (CRUD, Assistente, Planta 2D)
   - Filtro hierárquico reativo: `Empresa -> Prédio -> Andar`.

## Consequências
- **Positivas**:
  - Escalabilidade para grandes corporações multi-sede e multi-prédio.
  - Elimina lacunas funcionais com CRUDs completos e consistentes.
  - Preserva 100% de compatibilidade com os dados e testes existentes.
