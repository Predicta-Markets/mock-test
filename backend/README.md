# Backend (FastAPI)

## Stack

- FastAPI + Uvicorn
- SQLAlchemy 2.0 (async) with PostgreSQL
- Alembic migrations (`alembic/`)
- pytest for unit tests

## Local setup

```bash
cd capital-gains/backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Configure `DATABASE_URL` inside `.env` for either PostgreSQL or SQLite.

## Development server

```bash
uvicorn app.main:app --reload
```

## Order matching

The service keeps a simple limit order book per market (`order_book_levels` table):

- `BUY` orders are marketable. They first look for the lowest-price complementary orders on the opposite side and execute there. If there is not enough liquidity, the remainder executes immediately at the submitted price (effectively refunding the difference between the limit and matched price).
- `SELL` orders also cross existing liquidity, but any leftover quantity is parked on the book so future buyers can hit it. Resting entries keep their original price and FIFO order.
- Each executed request produces an `orders` row summarising the filled quantity, average fill price, realized P/L, and any residual `resting_quantity`.

This mirrors the behaviour described in the challenge brief: a YES order at 72 first tries to hit NO liquidity at the complementary 28. When none exists, it selects the next-highest NO level (e.g. 40) and refunds the difference by filling at 60/40 instead of 72/28.

## Database migrations

```bash
alembic upgrade head      # apply
alembic revision --autogenerate -m "message"  # create new migration
```

## Tests

```bash
pytest
```

The provided tests exercise the buy/sell flow, safeguards against overselling, and resolution logic.

