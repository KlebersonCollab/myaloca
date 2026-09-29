# Feature Specification: Documentação Central do Projeto & Galeria Visual (README)

## 1. User Stories
- **US-1 (Desenvolvedor / Avaliador Open Source)**: Como desenvolvedor ou avaliador visitando o repositório no GitHub, quero visualizar um README claro, atraente e completo com capturas de tela reais de alta resolução de todas as funcionalidades, para compreender instantaneamente a proposta de valor e a excelência do projeto.
- **US-2 (Engenheiro de Software)**: Como engenheiro iniciando no projeto, quero instruções simples de Quickstart para rodar o backend (`uv` / `python`) e o frontend (`npm`), além de credenciais predefinidas para testar diferentes permissões de usuário.
- **US-3 (Mantenedor do Projeto)**: Como mantenedor, quero um script automatizado de captura de telas que possa ser executado sob demanda para atualizar todas as capturas do README quando houver mudanças visuais na aplicação.

## 2. Business Rules & Invariants
- **BR-1 (Fidelidade Visual)**: As imagens contidas em `docs/screenshots/` devem ser capturas diretas da aplicação em tempo de execução real, sem montagens estáticas, placeholders vazios ou gráficos sintéticos.
- **BR-2 (Links Relativos)**: Todas as imagens referenciadas no `README.md` devem utilizar caminhos relativos portáveis (`docs/screenshots/<arquivo>.png`), assegurando compatibilidade nativa com o renderizador de Markdown do GitHub e clones locais.
- **BR-3 (Cobertura Integral de Funcionalidades)**: A documentação deve abranger os módulos principais: Gêmeo 3D WebGL, Planta 2D com Drag & Drop, Gestão de Facilities Multi-Edifício, Equipe com RBAC, Departamentos CRUD, Adesivos e Leitor de QR Code, e Minhas Reservas com Liberação Antecipada.
- **BR-4 (Conformidade SDD)**: O projeto deve validar integridade sem erros através dos scripts canônicos de governança.

## 3. Acceptance Criteria

### Cenário 1: Arquivo README.md Central
- **AC-1 (Existência e Estrutura do README)**:
  - *Given* a raiz do repositório,
  - *When* o arquivo `README.md` for inspecionado,
  - *Then* deve conter seções de Visão Geral, Galeria Visual, Tecnologias, Instalação, Credenciais e Licença.
- **AC-2 (Renderização de Imagens)**:
  - *Given* o arquivo `README.md`,
  - *When* for processado pelo GitHub ou visualizador Markdown,
  - *Then* todas as 11 imagens de `docs/screenshots/` devem resolver sem links quebrados.

### Cenário 2: Imagens Reais de Funcionalidades
- **AC-3 (Inventário de Capturas)**:
  - *Given* o diretório `docs/screenshots/`,
  - *When* for listado,
  - *Then* deve conter exatamente 11 arquivos PNG correspondentes às telas do sistema (3D overview, modal baia, 2d grid, edifícios, pavimentos, equipe, departamentos, adesivo QR, scanner QR, perfil avatar, minhas reservas).

### Cenário 3: Automação e Licenciamento
- **AC-4 (Script de Captura Funcional)**:
  - *Given* os servidores backend e frontend ativos,
  - *When* o script `node scripts/capture-screenshots.js` for executado,
  - *Then* todas as capturas são regeradas com sucesso sem erros.
- **AC-5 (Licença MIT)**:
  - *Given* a raiz do projeto,
  - *When* o arquivo `LICENSE` for lido,
  - *Then* deve conter o texto padrão da licença MIT.

## 4. Test Data Matrix
| Caso de Verificação | Comando / Caminho | Resultado Esperado |
|---|---|---|
| Existência do README | `Test-Path README.md` | `True` |
| Existência da Licença | `Test-Path LICENSE` | `True` |
| Verificação de Imagens | `Get-ChildItem docs/screenshots/*.png` | 11 arquivos válidos |
| Integridade SDD | `node .agents/scripts/verify-sdd-integrity.js` | 100% íntegro |
