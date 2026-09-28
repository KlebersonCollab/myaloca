# MyAloca Frontend: 3D Office & Hot-Desking SPA

Aplicação Single Page Application (SPA) desenvolvida em **Vue 3**, **Vite**, **TypeScript**, **Tailwind CSS** e **Three.js**, construída sob a estética minimalista e luxuosa da paleta **Linear Dark** ([`DESIGN.md`](../DESIGN.md)).

Permite visualizar o mapa do escritório tridimensionalmente, inspecionar onde os colegas de equipe estão sentados (com fotos e avatares flutuantes nas baias), agendar reservas com 1 clique diretamente na cena 3D e realizar validação presencial física através de scanner de QR Code.

---

## 🚀 Funcionalidades Principais

1. **🏢 Mapa Tridimensional Interativo do Escritório (Three.js WebGL)**:
   - Renderização das bancadas, monitores duplos e cadeiras ergonômicas em suas coordenadas espaciais reais `(x, y, z)`.
   - Câmera orbital fluida (OrbitControls: arraste para girar, scroll para zoom, botão para resetar vista).
   - Indicadores visuais de status com fitas de LED emissivas:
     - 🟢 **Verde** (`#27a644`): Baia Disponível para reserva imediata.
     - 🟡 **Âmbar** (`#eab308`): Baia Reservada (aguardando check-in do colaborador).
     - 🟣 **Roxo Linear** (`#5e6ad2`): Baia Ocupada (check-in presencial confirmado).
     - ⚫ **Cinza**: Em manutenção.
   - **Avatares & Fotos de Perfil**: Hologramas com a foto ou iniciais do colaborador flutuando sobre a baia ocupada.
   - Raycasting: Clique diretamente em qualquer baia para abrir a gaveta de detalhes e reserva.

2. **📅 Modal de Agendamento por Horário Livre**:
   - Seleção flexível de data e faixa horária (ex: 09:00 às 18:00).
   - Aviso automático da janela de tolerância de check-in (início + 30 min) para evitar no-show.
   - Detecção em tempo real de conflitos de reserva.

3. **📷 Scanner de Check-in Presencial com QR Code**:
   - Integração com a câmera do dispositivo via `html5-qrcode` para leitura do adesivo físico colado na mesa.
   - Fallback para inserção de código/token manual para testes rápidos em desktops.
   - Valida criptograficamente se o colaborador está de fato na baia física antes de confirmar a presença.

4. **🗂️ Painel "Minhas Reservas"**:
   - Lista as reservas ativas, históricas e expiradas do usuário logado.
   - Exibe o status atual e botão de acesso rápido para check-in.

5. **🛡️ Painel do Gestor de Facilities**:
   - Listagem técnica de todas as baias, zonas e coordenadas 3D.
   - Exportação e download em 1 clique do **QR Code imutável em PNG de alta resolução** pronto para impressão em adesivos físicos.
   - Cadastro de novas baias definindo coordenadas espaciais `(x, y, z)` e equipamentos.

6. **🔄 Alternador de Perfil Demo em 1 Clique**:
   - Botão no cabeçalho para alternar instantaneamente entre a visão de **Gestor** (`admin@myaloca.com`) e **Colaborador** (`colaborador@myaloca.com`) sem necessidade de digitar credenciais.

---

## 🛠️ Stack Tecnológica

- **Framework**: [Vue 3](https://vuejs.org/) (Composition API, `<script setup lang="ts">`)
- **Build Tool**: [Vite](https://vite.dev/)
- **Linguagem**: TypeScript
- **Renderizador 3D**: [Three.js](https://threejs.org/) (WebGL, OrbitControls, Raycaster, CanvasTexture)
- **Design System & Estilização**: [Tailwind CSS](https://tailwindcss.com/) configurado com os tokens do Linear Dark (`DESIGN.md`)
- **Ícones**: [Lucide Icons](https://lucide.dev/) (`lucide-vue-next`)
- **Scanner de QR Code**: `html5-qrcode`

---

## 💻 Como Executar Localmente

### 1. Pré-requisitos
Certifique-se de que o **Backend FastAPI** está rodando em [http://localhost:8000](http://localhost:8000).

### 2. Instalar Dependências
Dentro da pasta `frontend/`:

```bash
npm install
```

### 3. Iniciar Servidor de Desenvolvimento
```bash
npm run dev
```

Abra seu navegador em [http://localhost:5173](http://localhost:5173).

---

## 📦 Build para Produção

Para gerar o bundle estático otimizado para deploy:

```bash
npm run build
```

Os arquivos de distribuição serão gerados na pasta `frontend/dist/`.
