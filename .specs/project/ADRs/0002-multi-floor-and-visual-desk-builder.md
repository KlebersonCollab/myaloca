# ADR 0002: Suporte a Edifícios Multi-Andares e Construtor Visual de Baias Sem Coordenadas Manuais

## Status
Accepted

## Contexto
Em edifícios comerciais corporativos, prédios possuem N andares e diversos setores por pavimento. Exigir que o gestor ou administrador de facilities preencha manualmente coordenadas 3D cartesianas (X, Y, Z) é impraticável e gera atrito severo. O sistema deve permitir:
1. Navegação e gestão de múltiplos andares (Térreo, 1º Andar, 2º Andar, ..., N Andar) de forma fluida.
2. Criação simplificada de baias sem exigir conhecimento de eixos matemáticos, através de um assistente de bancadas/fileiras e posicionamento visual interativo por clique.

## Decisão
1. **Hierarquia de Pavimentos e Setores (Multi-Floor)**:
   - Utilizar a entidade `Zone` para modelar pavimentos com atributo `floor: int` e `name: str` (ex: "Andar 2 - Engenharia").
   - Atualizar endpoints `/api/v1/bookings/3d-office`, `/api/v1/desks` e `/api/v1/zones` para suportar filtragem direta por `floor` e `zone_id`.
   - Permitir ao gestor cadastrar novos andares e setores rapidamente com nome e número do piso.
2. **Assistente de Layout Automático (Grid & Row Builder)**:
   - O gestor seleciona o Andar, a Fileira/Bancada (ex: Letra A, B, C) e o estilo (Frente a frente ou fileira simples).
   - O algoritmo calcula automaticamente as coordenadas espaciais com espaçamento ergonômico padrão de escritório (2.2m de largura e 2.5m de profundidade) e rotações de 0° e 180° para colaboradores sentados de frente um para o outro.
   - Suporte à geração individual ou em lote (ex: bancada com 4 ou 6 baias) com geração automática de tokens QR Code imutáveis.
3. **Grade Visual Interativa 2D (Click-to-Place)**:
   - Exibir uma planta esquemática do andar onde o gestor clica numa célula vazia para posicionar uma baia no mapa com coordenadas mapeadas automaticamente.
4. **Seletor de Andares na Experiência 3D**:
   - No mapa 3D (`OfficeCanvas3D.vue`), adicionar seletor de pavimentos do edifício para alternar a visão entre andares de forma instantânea.

## Consequências
- **Positivas**:
  - Elimina 100% da fricção de coordenadas manuais para o gestor.
  - Permite escalar o software para edifícios comerciais de qualquer porte com dezenas de andares.
  - As baias ficam perfeitamente alinhadas e com rotação realista no mapa 3D.
