## BalanceHub

Async REST API for managing users, accounts and payments.

### Tech
- FastAPI, SQLAlchemy (async), Alembic
- PostgreSQL
- Pydantic, pydantic-settings
- Docker Compose

### Run with Docker Compose
1. Copy env example:
   ```bash
   cp .env.example .env
   ```
2. Start:
   ```bash
   docker compose up --build
   ```
3. API will be available at `http://localhost:8000` and docs at `http://localhost:8000/docs`.

Default users (created by migration):
- User: `user@example.com` / `Password123!`
- Admin: `admin@example.com` / `Admin123!`

### Run locally (without Docker)
1. Start PostgreSQL and create DB `balancehub`.
2. Copy `.env.example` to `.env` and set `DATABASE_URL` and `SYNC_DATABASE_URL` to localhost.
3. Install deps:
   ```bash
   poetry install
   ```
4. Run migrations:
   ```bash
   poetry run alembic upgrade head
   ```
5. Start app:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Webhook signature
Signature is SHA256 of concatenated values in alphabetical order of keys plus secret key:
```
{account_id}{amount}{transaction_id}{user_id}{secret_key}
```

Example secret key `gfdmhghif38yrf9ew0jkf32`.

### OpenAPI
Explore and test all endpoints at `/docs`. Includes authentication, users (admin), accounts, payments, and webhook.
