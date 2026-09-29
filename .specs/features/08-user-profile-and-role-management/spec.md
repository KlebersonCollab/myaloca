# Feature Specification: Edição de Perfil, Cargos e Gestão de Usuários

## 1. Requisitos Funcionais

- **FR-1**: O usuário logado deve poder atualizar seu perfil (nome, cargo, departamento, avatar 3D e foto) via `PUT /api/v1/auth/me`.
- **FR-2**: O usuário logado não pode alterar seu próprio `role` via `PUT /api/v1/auth/me`.
- **FR-3**: Administradores devem poder listar todos os usuários com suporte a filtro por papel e busca textual via `GET /api/v1/users`.
- **FR-4**: Administradores devem poder cadastrar novos usuários com cargo e papel definidos via `POST /api/v1/users`.
- **FR-5**: Administradores devem poder atualizar cargo, departamento, papel e status ativo de qualquer usuário via `PUT /api/v1/users/{id}`.
- **FR-6**: Administradores não podem excluir ou desativar sua própria conta via `DELETE /api/v1/users/{id}` (erro `CANNOT_DELETE_SELF`).
- **FR-7**: A interface deve disponibilizar formulário de edição de perfil na aba de usuário e uma tela administrativa dedicada de gestão de cargos e papéis da equipe.

## 2. Critérios de Aceite (BDD)

### Cenário 1: Edição do próprio perfil pelo colaborador
- **Dado** que um colaborador autenticado envia `PUT /api/v1/auth/me` com `job_title="Senior Frontend Dev"` e `department="Produto"`
- **Quando** a requisição for processada
- **Então** o status de resposta deve ser 200 OK
- **E** os novos dados devem ser refletidos imediatamente na sessão do usuário e na maquete 3D.

### Cenário 2: Tentativa de alteração de cargo e papel por não-administrador
- **Dado** que um colaborador tenta acessar `GET /api/v1/users` ou `PUT /api/v1/users/{id}`
- **Quando** a requisição for executada
- **Então** o status retornado deve ser 403 Forbidden.

### Cenário 3: Administrador altera cargo e promove usuário a Gestor
- **Dado** que um administrador envia `PUT /api/v1/users/{id}` com `role="gestor"` e `job_title="Coordenador de TI"`
- **Quando** a requisição for processada
- **Então** o status retornado deve ser 200 OK
- **E** o usuário promovido passa a ter acesso liberado às salas de reunião exclusivas para gestores.

### Cenário 4: Bloqueio de auto-exclusão do administrador
- **Dado** que o administrador logado envia `DELETE /api/v1/users/{id}` com seu próprio `id`
- **Quando** a requisição for processada
- **Então** o status retornado deve ser 400 Bad Request com código `CANNOT_DELETE_SELF`.
