# Glossário do Domínio: MyAloca (Desk & Hot-Desking System)

## Conceitos Centrais de Negócio

### 1. Baia (Desk / Workstation)
Ponto físico individual de trabalho localizado em uma zona ou andar do escritório.
- **Atributos**: Código identificador único (ex: `BAIA-A101`), Zona/Andar, Coordenadas espaciais 3D `(x, y, z)`, Status (`DISPONIVEL`, `RESERVADA`, `OCUPADA`, `MANUTENCAO`), Recursos adicionais (monitores extras, docking station, etc.).
- **QR Code Físico**: Cada baia possui um código QR imutável impresso e afixado na bancada para validação presencial.

### 2. Colaborador (User)
Membro da organização sujeito à política de trabalho híbrido ou gestor da unidade.
- **Perfil**: Nome, e-mail corporativo, cargo, departamento, foto de perfil (upload) e preferências/avatar 3D configurável.
- **Papéis (Roles)**:
  - `Colaborador`: Consulta o mapa 3D, reserva baias, realiza check-in presencial, visualiza colegas no escritório.
  - `Gestor / Administrador`: Cadastra zonas e baias, ajusta coordenadas 3D, exporta lotes de QR Codes para impressão, configura janelas de check-in e limites de antecedência, audita relatórios de no-show.

### 3. Reserva (Booking)
Agendamento com antecedência de uma baia específica para uma data e período (dia completo ou turnos manhã/tarde).
- **Ciclo de Vida**:
  - `PENDENTE_CHECKIN`: Reserva criada com antecedência; aguarda o colaborador chegar presencialmente à baia.
  - `CHECKED_IN` / `EM_USO`: Colaborador escaneou o QR Code da baia dentro da janela permitida; baia ocupada com avatar 3D do colaborador ativo.
  - `CANCELADA_USUARIO`: Cancelamento voluntário antes do início ou do limite.
  - `EXPIRADA_NO_SHOW`: Colaborador não realizou check-in até o horário limite; a reserva é cancelada pelo sistema automaticamente e a baia é liberada.
  - `FINALIZADA`: Fim do expediente/período reservado.

### 4. Check-in Presencial e Tolerância (Check-in Window & No-Show)
Mecanismo de garantia de uso efetivo do espaço físico em modelo híbrido.
- **Horário Limite de Check-in**: Regra parametrizável (ex: até 09:30 no período matutino ou tolerância de até 30 minutos após o horário de início da reserva).
- **Auto-Release (Liberação Automática)**: Processo em background que cancela reservas que não tiveram check-in até o horário de corte, liberando a baia para reservas imediatas por outros colaboradores.

### 5. QR-Code Imutável de Baia
Identificador criptográfico e estável atribuído à baia.
- **Geração e Impressão**: Gestor gera e exporta (PDF / PNG em vetor/alta resolução) os QR Codes para impressão em adesivos/placas físicas.
- **Validação**: Ao apontar a câmera do celular/aplicativo web, o payload do QR Code valida criptograficamente que o colaborador está de fato em frente àquela baia específica.

### 6. Mapa 3D do Escritório (3D Office Canvas)
Visualização tridimensional interativa do andar ou zona de trabalho.
- **Renderização**: Baias posicionadas em coordenadas tridimensionais, iluminação, visualização em perspectiva/isométrica.
- **Avatares e Fotos**: Quando uma baia está reservada ou ocupada, exibe o avatar tridimensional ou badge holográfico com a foto do colaborador sobre o assento correspondente.
- **Interatividade**: Permite girar, dar zoom, clicar em baias livres para reservar ou inspecionar quem está sentado em cada posição.
