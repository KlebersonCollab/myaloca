# Code Conventions & Idioms

## Naming Standards
- **Python**:
  - Files / Modules: `snake_case.py`
  - Classes / Exceptions: `PascalCase`
  - Functions / Methods / Variables: `snake_case`
  - Constants: `SCREAMING_SNAKE_CASE`
  - Pydantic Schemas: `PascalCase` com sufixos explícitos (ex: `DeskCreate`, `DeskResponse`, `DeskUpdate`)
- **Frontend (TypeScript)**:
  - Files / Components: `PascalCase.tsx`
  - Utilities / Hooks: `camelCase.ts`
  - Constants: `SCREAMING_SNAKE_CASE`

## Error Handling
- Use exceções HTTP padronizadas via `HTTPException` do FastAPI com payloads estruturados:
  ```python
  raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail={"code": "BOOKING_CONFLICT", "message": "Baia já reservada para o período selecionado."}
  )
  ```
- Nunca engula exceções silenciosamente; todo `try/except` deve registrar log ou relançar.

## Formatting & Imports
- **Backend**:
  - Linter & Formatter: `ruff` (linha máxima de 100 caracteres).
  - Ordem de importação: Standard Library -> Bibliotecas Externas -> Módulos Internos da aplicação (`from app...`).
- **Frontend**:
  - Design Tokens alinhados estritamente com `DESIGN.md` (Linear Dark palette).

## Async Standards
- Todas as operações de I/O (Database queries, uploads de arquivo, chamadas externas) DEVEM ser declaradas como `async def` e utilizar `await`.
- Nunca use chamadas síncronas bloqueantes dentro do event loop do FastAPI.
