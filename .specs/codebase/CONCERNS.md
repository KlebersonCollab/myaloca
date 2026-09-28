# Critical Risks & Invariants (CONCERNS)

## High-Risk Areas & Business Invariants

### 1. Concorrência e Race Conditions no Agendamento de Baias
- **Risco**: Dois colaboradores tentarem reservar a mesma baia exatamente no mesmo segundo para a mesma data.
- **Mitigação**:
  - Restrição única no banco de dados (`UniqueConstraint('desk_id', 'date', 'period')` onde status seja ativo).
  - Transação atômica no banco de dados com commit/rollback estrito.

### 2. Sincronização e Drift do Scheduler de No-Show
- **Risco**: Scheduler não rodar ou perder reservas pendentes após reinicialização da aplicação.
- **Mitigação**:
  - O scheduler deve ser baseado no relógio e no estado persistido no banco de dados (`Booking.status == PENDENTE_CHECKIN` e `Booking.checkin_deadline <= now()`), sem depender de timers em memória volátil.

### 3. Falsificação ou Fraude de Check-in Presencial
- **Risco**: Colaborador compartilhar foto do QR Code com outro colega para forjar presença sem estar fisicamente na empresa.
- **Mitigação**:
  - O QR-Code físico da baia possui um identificador criptográfico imutável único gerado pelo gestor.
  - Para validação avançada, pode-se registrar o IP da rede Wi-Fi corporativa ou geolocalização no momento da leitura.

### 4. Coordenadas 3D e Desempenho WebGL
- **Risco**: Cenas com centenas de baias e avatares gerando quedas de FPS no navegador.
- **Mitigação**:
  - Uso de instanced meshes (Three.js `InstancedMesh`) para as geometrias das mesas/cadeiras idênticas.
  - Carregamento de avatares com LOD (Level of Detail) ou sprites/billboards leves com a foto do usuário.
