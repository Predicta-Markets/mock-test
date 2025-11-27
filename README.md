# Mock Prediction Market Platform

This challenge is now a **full-stack** exercise. Build a minimal prediction market where users can create markets, place YES/NO orders, and resolve outcomes. Focus on core **buy/sell logic**, **no authentication**, and **no tax calculation**. The final submission must include a FastAPI backend, a Next.js frontend styled with shadcn/ui, and a Docker Compose stack running the entire system with PostgreSQL.


## 🚀 Quick Start

**How to Use**: See [USER_GUIDE.md](./USER_GUIDE.md) for a simple explanation of what this is and how to use it.

**For developers**: Follow these steps to get started:

1. Clone this repo

2. **Prerequisites**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

3. **Start the application**:
   ```bash
   cd mock-test
   docker compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8005/docs
   - Backend API: http://localhost:8005

5. **Stop the application**:
   ```bash
   docker compose down
   ```

The Docker Compose setup automatically:
- Runs database migrations on startup
- Enables live reload for both frontend and backend
- Sets up all necessary environment variables

**Note**: No `.env` files are required - everything is configured in `compose.yml`. The `.env.example` files are provided for reference if you want to run services individually.

## 1. Architecture Overview

```
┌──────────┐      REST       ┌────────────┐
│ Next.js  │ <─────────────> │ FastAPI    │
│ (shadcn) │                 │ SQLAlchemy │
└────┬─────┘                 └────┬───────┘
     │     docker network           │
     │                               │
     ▼                               ▼
 ┌────────┐   Postgres + Alembic   ┌────────┐
 │ docker │ ---------------------> │  db    │
 └────────┘                        └────────┘
```

- **Frontend**: Single-page experience built with Next.js 14+ App Router. Use shadcn/ui components for form inputs, tables, and modals. Fetch data via TanStack Query.
- **Backend**: FastAPI app exposing JSON endpoints. Persistence handled via SQLAlchemy (prefer async engine) and Alembic migrations.
- **Database**: PostgreSQL storing markets, orders, and holdings. Use UUID primary keys, timestamp columns, and state enums.

## 2. Backend Requirements

### 2.1 Tech stack

- Python 3.11+
- FastAPI, uvicorn, Pydantic v2
- SQLAlchemy 2.0 (async recommended) with Alembic migrations
- PostgreSQL 15+
- pytest for unit tests
- Limit-order matching: BUY requests cross the resting order book and fill at the nearest complementary price at or above the theoretical complement. SELL requests post liquidity when no counterpart is available. Remaining volume is persisted in `order_book_levels` so subsequent trades honour price/age priority.

### 2.2 Data model (minimum)

| Table         | Key fields                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------ |
| `markets`     | `id`, `slug`, `question`, `description`, `status` (`OPEN`, `RESOLVED`), `outcome` (`YES/NO/null`), timestamps |
| `orders`      | `id`, `market_id`, `side` (`YES/NO`), `price` (0–100), `quantity`, `type` (`BUY`/`SELL`), `total_cost`, timestamps |
| `positions`   | `id`, `market_id`, `side`, `average_price`, `quantity`, timestamps                               |
| `resolutions` | `id`, `market_id`, `outcome`, `payout_yes`, `payout_no`, timestamps                               |

You may extend the schema with additional helper tables if it simplifies the business logic (e.g., trade ledger, snapshots).

### 2.3 Business rules

1. **Complementary prices**: YES price + NO price must equal 100. Reject invalid orders.
2. **Inventory guardrails**: Cannot sell more contracts than currently held for that side. Return a 422 error if violated.
3. **Weighted average cost**: Buying increases `quantity` and recalculates the average price per side:  
   `new_avg = ((old_qty * old_avg) + (new_qty * new_price)) / (old_qty + new_qty)`
4. **Selling**: Decrease quantity using the current average cost. Track realized P/L for display, but **do not** compute taxes.
5. **Resolution**: When a market resolves to YES or NO, calculate payout for remaining holdings: winning side receives 100 cents per contract; losing side receives 6. Persist final state and prevent further trades.

### 2.4 API surface (suggested)

```
GET    /markets
POST   /markets                 body: { question, description?, slug?, initial_price_yes? }
GET    /markets/{id}
POST   /markets/{id}/orders     body: { side: "YES"|"NO", type: "BUY"|"SELL", price, quantity }
POST   /markets/{id}/resolve    body: { outcome: "YES"|"NO" }
GET    /markets/{id}/positions  -> aggregated holdings & realized P/L
GET    /healthz
```

Feel free to add endpoints (e.g., `/orders`, `/positions`) as long as the core flows above work.

### 2.5 Testing

- Provide targeted unit tests in `mock-test/backend/tests/` covering:
  - Weighted-average calculation.
  - Preventing oversells.
  - Proper state changes during resolution.
  - At least one API test hitting `/markets/{id}/orders`.

## 3. Frontend Requirements

### 3.1 Tech stack

- Next.js 14+ App Router (TypeScript, strict mode).
- Tailwind CSS with `postcss.config.js` + `tailwind.config.ts`.
- shadcn/ui for ready-made components (`Button`, `Card`, `Dialog`, `Table`, `Form`, etc.).
- TanStack Query for data fetching + cache.
- Axios or fetch wrapper for HTTP calls.

### 3.2 Features

1. **Market list**
   - Display question, status (badge), and aggregate YES/NO prices.
   - CTA to create a new market (modal or separate page).
2. **Market detail**
   - Show question, description, current holdings for YES/NO, remaining inventory.
   - Forms for BUY and SELL with validation (side, price, quantity).
   - Table of recent orders (optional but encouraged).
   - Button to resolve market (disabled when already resolved) plus outcome selector.
3. **Holdings summary**
   - Show aggregated YES/NO positions, average cost, and unrealized P/L.
4. **UX expectations**
   - Loading and error states for each mutation.
   - Optimistic updates or immediate refetch after actions.
   - Responsive layout (desktop + mobile).

### 3.3 shadcn setup

- Use the standard `npx shadcn-ui@latest init`.
- Include at least `button`, `card`, `table`, `form`, `input`, `select`, and `dialog`.
- Keep styling consistent with Predicta brand (Tailwind + semantic colors).

## 4. Docker Compose Environment

Create `mock-test/compose.yml` with three services:

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: predicta
      POSTGRES_USER: predicta
      POSTGRES_PASSWORD: predicta
    volumes:
      - db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    environment:
      DATABASE_URL: postgresql+asyncpg://predicta:predicta@db:5432/predicta
    volumes:
      - ./backend:/app
    depends_on:
      - db
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    command: pnpm dev --host 0.0.0.0 --port 3000
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  db-data:
```

Guidelines:
- Bind-mount backend/frontend source directories to enable live reload.
- Ensure backend waits for PostgreSQL (use `depends_on` + retry logic or a wait script).
- Provide `.env.example` files for both backend and frontend describing required variables (DB URL, API URL, etc.).

---

## 5. Running & Development Workflow

### Basic Usage

1. **Start everything**:
   ```bash
   cd mock-test
   docker compose up --build
   ```
   - Migrations run automatically on backend startup
   - All services have live reload enabled
   - No `.env` files needed (configured in `compose.yml`)

2. **Access the application**:
   - Frontend: http://localhost:3000
   - API: http://localhost:8005
   - API Docs: http://localhost:8005/docs

3. **Stop everything**:
   ```bash
   docker compose down
   ```

### Development Commands

**Run backend tests**:
```bash
docker compose exec backend pytest
```

**Run frontend lint/tests**:
```bash
docker compose exec frontend pnpm lint
docker compose exec frontend pnpm test
```

**Manual migration** (if needed):
```bash
docker compose exec backend alembic upgrade head
```

**View logs**:
```bash
docker compose logs -f [service_name]  # e.g., backend, frontend, db
```

### Running Services Individually [Not recommended]

If you prefer to run services outside Docker:

1. **Backend**: Copy `backend/.env.example` to `backend/.env` and run:
   ```bash
   cd backend
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

2. **Frontend**: Copy `frontend/.env.example` to `frontend/.env` and run:
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

3. **Database**: Use the Docker Compose database or set up PostgreSQL locally.

