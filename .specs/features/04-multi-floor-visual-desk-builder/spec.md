# Specification: Suporte a Prédios Multi-Andares e Construtor Visual de Baias Sem Coordenadas Manuais

## 1. Feature Overview
Permite gerenciar múltiplos andares em prédios corporativos e cadastrar baias de forma intuitiva sem exigir conhecimento de eixos matemáticos 3D, utilizando assistente de bancadas e posicionamento visual em grade.

## 2. Acceptance Criteria (BDD)

### Scenario 1: Navegação entre Múltiplos Andares no Mapa 3D
- **Given** que o sistema possui múltiplos andares cadastrados (ex: Andar 1, Andar 2, Andar 3),
- **When** o usuário seleciona um andar no topo da visualização 3D,
- **Then** a cena WebGL é atualizada para exibir exclusivamente as baias pertencentes às zonas daquele andar com seus respectivos status e ocupantes.

### Scenario 2: Criação de Bancada Assistida Sem Coordenadas Manuais
- **Given** que o gestor deseja criar uma nova bancada de trabalho,
- **When** ele seleciona o Andar, a Fileira (ex: "Bancada B") e a quantidade de baias (ex: 4),
- **Then** o sistema gera as baias `B-01` a `B-04` com posições `(x, y, z)` calculadas automaticamente com espaçamento ergonômico e tokens QR imutáveis gerados.

### Scenario 3: Posicionamento Visual por Clique na Grade 2D
- **Given** que o gestor está no modo de Grade Visual do Andar,
- **When** ele clica sobre uma célula vazia da planta,
- **Then** uma nova baia é alocada naquela posição correspondente sem que o usuário tenha digitado números cartesianos.

### Scenario 4: Cadastro Rápido de Novo Andar ou Setor
- **Given** que o gestor precisa expandir a capacidade para um novo pavimento,
- **When** ele informa o número do andar (ex: 4) e o nome do setor (ex: "4º Andar - Inovação"),
- **Then** a nova zona é persistida e fica imediatamente disponível nos seletores e filtros.
