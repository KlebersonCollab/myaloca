# MyAloca: Sistema de Gestão & Agendamento de Baias Híbridas 3D

## Visão Geral do Produto
O **MyAloca** é uma plataforma moderna e imersiva para escritórios com regime de trabalho híbrido. A solução resolve o problema de ociosidade e falta de previsibilidade de espaço físico através de reserva antecipada de baias, fiscalização presencial de presença via QR Code físico nas bancadas, liberação automática de assentos por no-show (tolerância com auto-release) e uma experiência rica e imersiva com mapa 3D do escritório mostrando fotos e avatares dos colegas de equipe.

## Objetivos Principais
1. **Otimização do Espaço Físico**: Garantir que baias reservadas sejam efetivamente utilizadas, liberando assentos automaticamente caso o colaborador não faça check-in presencial no horário estipulado.
2. **Confirmação Presencial Física**: QR-Codes imutáveis impressos e colados em cada baia para check-in imediato através do app mobile/web.
3. **Imersão Espacial 3D**: Visão tridimensional interativa do andar do escritório, onde colaboradores visualizam onde seus pares de equipe estão sentados com avatares e fotos de perfil.
4. **Painel de Gestão Completo**: Ferramenta administrativa para cadastro de baias, parametrização de coordenadas espaciais, configuração de regras de tolerância e exportação de lotes de QR Codes para impressão.
5. **Arquitetura de Alta Performance**: Backend assíncrono em Python (FastAPI), SQLAlchemy 2.0 Async, modelagem desacoplada com compatibilidade SQLite (dev local ágil) e PostgreSQL (produção resiliente).

## Stakeholders e Personas
- **Colaborador Híbrido**: Precisa saber quais dias ir ao escritório, reservar baia próxima ao seu time, fazer check-in rápido via QR Code e saber quem estará presencial no mesmo dia.
- **Gestor de Facilities / RH / Operações**: Precisa cadastrar o layout do escritório, imprimir identificadores físicos QR, evitar reservas fantasmas e analisar taxas de ocupação.
