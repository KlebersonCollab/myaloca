# Feature Plan: Documentação Central do Projeto & Galeria Visual (README)

## 1. Visão Geral
Esta funcionalidade consolida a documentação de referência para publicação do projeto **MyAloca** no GitHub. Inclui:
1. **README Central Completo**: Documento em Markdown com badges modernos, visão geral do produto, diferenciais técnicos, arquitetura em árvore, guia rápido de instalação e credenciais de demonstração.
2. **Galeria Visual com Imagens Reais**: Capturas reais de tela em alta resolução (`docs/screenshots/*.png`) geradas diretamente da aplicação em execução (frontend na porta 5173 e backend na porta 8000), cobrindo 100% das funcionalidades do sistema sem uso de mocks ou ilustrações sintéticas.
3. **Script de Automação de Capturas**: Ferramenta automatizada headless (`scripts/capture-screenshots.js`) com Playwright/Puppeteer para captura determinística das telas com diferentes sessões de usuários (`admin` e `mariana`).
4. **Licença de Código Aberto**: Inclusão de licença permissiva MIT (`LICENSE`).

## 2. Escopo da Solução

### 2.1 Documentação e Ativos Visuais
- **README Central (`README.md`)**:
  - Cabeçalho com insígnias oficiais das tecnologias empregadas.
  - Galeria visual com 11 imagens reais comentadas e contextualizadas.
  - Detalhamento dos pilares de engenharia: Gêmeo Digital 3D (Three.js), Matriz 2D Flexível e Adaptativa, QR Code Físico e Antifraude, Política de Tolerância e Auto-Release por No-Show.
  - Mapeamento da árvore de diretórios e tabela de tecnologias.
  - Passo a passo de instalação com `uv` e `npm`.
  - Matriz de credenciais para testes com diferentes papéis corporativos.
  - Comandos para execução de testes unitários e sensores de integridade SDD.
- **Ativos Visuais (`docs/screenshots/`)**:
  - 11 capturas em resolução @2x cobrindo: 3D Overview, Detalhe da Baia 3D, Planta Baixa 2D, Edifícios de Facilities, Pavimentos de Facilities, Equipe & RBAC, Departamentos Corporativos CRUD, Adesivo Físico QR Code, Scanner de Check-in, Perfil com Avatar DiceBear, Minhas Reservas & Liberação Antecipada.
- **Licenciamento (`LICENSE`)**:
  - Termos MIT completos de 2026.

### 2.2 Automação e Ferramentas
- **Script de Captura (`scripts/capture-screenshots.js`)**:
  - Script em Node.js com `puppeteer-core` apontando para o binário Chromium local.
  - Autenticação e injeção de tokens JWT para simular administradores e colaboradores.
  - Interação automatizada com elementos do DOM, botões de navegação, modais e canvas WebGL Three.js.

## 3. Riscos e Mitigações
- **Qualidade e Estabilidade das Imagens**: Execução automatizada com viewport de 1920x1080 e fator de escala @2x garante imagens nítidas em telas Retina e renderização uniforme no GitHub.
- **Spec Drift**: Todos os arquivos de documentação, automação e dependências adicionadas são formalmente catalogados na especificação canônica SDD.
