# Feature Plan: Edição de Perfil, Cargos e Gestão de Usuários

## 1. Visão Geral
Esta feature provê tanto a autonomia individual (self-service) para os colaboradores editarem seus perfis, cargos, departamentos, fotos e avatares 3D, quanto a governança corporativa para administradores e gestores gerenciarem os papéis de acesso (`admin`, `gestor`, `colaborador`), cargos corporativos (`job_title`) e status de contas da equipe.

## 2. Escopo da Solução

### 2.1 Backend
- **Schemas**:
  - `AdminUserCreate`: criação direta de usuário por admin com definição de `role`, `job_title`, `department`, etc.
  - `AdminUserUpdate`: atualização administrativa de cargo, departamento, role, status ativo e dados cadastrais.
- **Serviço e Endpoints de Usuários (`/api/v1/users`)**:
  - `GET /api/v1/users`: listar colaboradores com busca por nome/email e filtro por papel.
  - `GET /api/v1/users/{id}`: obter detalhes de usuário.
  - `POST /api/v1/users`: criar novo colaborador com cargo e papel.
  - `PUT /api/v1/users/{id}`: editar cargo, departamento, papel e status.
  - `DELETE /api/v1/users/{id}`: excluir ou desativar usuário com trava de auto-exclusão.
- **Roteador**: registro de `users.router` em `app/api/v1/router.py`.

### 2.2 Frontend
- **Edição de Perfil Pessoal (`AuthView.vue`)**:
  - Modo de edição integrado na aba "Meu Perfil", permitindo alterar Nome, Cargo (`job_title`), Departamento, Avatar 3D e Foto real.
  - Atualização síncrona na store de autenticação.
- **Módulo de API (`frontend/src/services/api.ts`)**:
  - Métodos `api.users.list`, `api.users.get`, `api.users.create`, `api.users.update`, `api.users.delete` e `api.auth.updateMe`.
- **Tela Administrativa de Equipe & Cargos (`AdminUsersView.vue`)**:
  - Listagem completa dos colaboradores.
  - Seletor de papéis com explicações (Colaborador, Gestor de Facilities, Administrador Geral).
  - Modal para alteração rápida de Cargo (`job_title`) e Nível de Acesso (`role`).
  - Modal para cadastro rápido de novo membro da equipe.
- **Navegação (`Navbar.vue` e `App.vue`)**:
  - Inclusão do link "Equipe & Cargos" no menu superior para perfis `admin` e `gestor`.

## 3. Riscos e Mitigações
- **Escalada de Privilégios**: `PUT /auth/me` não permite alterar o próprio `role`. Apenas administradores através de `PUT /api/v1/users/{id}` podem alterar papéis.
- **Auto-Exclusão**: A exclusão do próprio usuário logado é terminantemente bloqueada no backend (`CANNOT_DELETE_SELF`).
