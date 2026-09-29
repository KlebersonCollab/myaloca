# ADR 0006: Gestão e Edição de Perfil de Usuário, Cargos e Papéis Corporativos

## Status
Accepted

## Data
2026-09-28

## Contexto
O sistema MyAloca já possui suporte a restrições de reservas por perfil (como salas especiais restritas a gestores através de `required_role: 'gestor'`), modelos de dados com `job_title` e `department`, e endpoint básico de `PUT /auth/me`. No entanto:
1. O usuário logado não possui formulário visual na interface para editar seus dados pessoais, cargo (`job_title`), departamento, avatar 3D ou foto.
2. Não existe endpoint nem tela administrativa para gestores/administradores gerenciarem a equipe: listar usuários, atribuir e alterar papéis corporativos (`admin`, `gestor`, `colaborador`), editar cargos de outros colaboradores ou cadastrar novos membros com seus respectivos papéis.

## Decisão Arquitetural
1. **Endpoint de Gestão de Usuários (`/api/v1/users`)**:
   - Criação de `backend/app/api/v1/endpoints/users.py` protegido por dependência RBAC (`get_current_admin`).
   - Métodos:
     - `GET /api/v1/users`: Listagem de usuários com suporte a filtro por role e busca por termo.
     - `GET /api/v1/users/{id}`: Obtenção detalhada de um usuário.
     - `POST /api/v1/users`: Cadastro direto de colaborador com definição explícita de `role`, `job_title` e `department`.
     - `PUT /api/v1/users/{id}`: Atualização de cargo, departamento, papel e status ativo.
     - `DELETE /api/v1/users/{id}`: Desativação ou exclusão segura (com trava impedindo auto-exclusão do admin logado).
2. **Edição do Próprio Perfil (`PUT /api/v1/auth/me`)**:
   - Expansão da interface em `AuthView.vue` com formulário interativo de edição ("Editar Perfil"), permitindo ao usuário alterar em tempo real seu nome, cargo, departamento, avatar 3D (presets DiceBear) e foto personalizada.
   - Sincronização reativa com a store `useAuth()`.
3. **Visão Administrativa de Equipe e Cargos (`AdminUsersView.vue`)**:
   - Criação de uma tela dedicada de gestão de pessoas e permissões no frontend, acessível a gestores e administradores pelo Navbar.
   - Tabela com filtros rápidos por papel, métricas de equipe e modal para edição de cargos e permissões de acesso.

## Consequências
- **Positivas**:
  - Controle corporativo granular: administradores podem promover colaboradores a `gestor` para acessar salas reservadas ou `admin` para gerenciar facilities.
  - Colaboradores têm autonomia para personalizar sua identidade digital (cargo, foto, avatar 3D exibido na maquete WebGL).
  - Trava de auto-exclusão garante que a administração do sistema nunca seja trancada acidentalmente.
- **Negativas / Cuidados**:
  - O endpoint `PUT /users/{id}` deve ser restrito exclusivamente a administradores para impedir escalada de privilégios não autorizada.
