# Capital Gains - Project Overview

## What Is This?

**Capital Gains** is a **prediction market platform** - a web application where you can create markets, trade shares, and resolve outcomes.

Think of it like a stock market for future events. Instead of buying shares in companies, you buy shares in whether something will happen or not.

## Simple Example

**Market Question**: "Will it rain tomorrow?"

- You can buy **YES shares** (betting it WILL rain) at, say, 60 cents
- Or buy **NO shares** (betting it WON'T rain) at 40 cents
- If it rains: YES shares pay 100 cents, NO shares pay 0 cents
- If it doesn't rain: NO shares pay 100 cents, YES shares pay 0 cents

The prices change based on what people think will happen!

## What Can You Do?

1. ✅ **Create Markets** - Ask any yes/no question
2. ✅ **Buy Shares** - Invest in YES or NO outcomes
3. ✅ **Sell Shares** - Exit your position anytime
4. ✅ **Track Profits** - See your gains and losses
5. ✅ **Resolve Markets** - Determine winners and payouts

## How Does It Work?

### The Basics

- Every market has **two sides**: YES and NO
- Prices always add up to **100 cents** (if YES = 70, NO = 30)
- You can **buy** shares (if you think the price will go up)
- You can **sell** shares (if you want to take profits or exit)
- When the event happens, the market **resolves** and pays out

### The Trading System

When you place an order:
1. The system tries to **match** you with someone on the other side
2. If matched, you trade immediately at the best available price
3. If not matched, your order waits in the **order book** for later
4. Prices **update automatically** based on completed trades

### Position Tracking

The system remembers:
- How many shares you own (YES and NO separately)
- What you paid on average (weighted average cost)
- Your profit/loss from trades you've made

## Technology Stack

- **Frontend**: Next.js (React) with TypeScript
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Deployment**: Docker Compose

## Getting Started

### For End Users

See [USER_GUIDE.md](./USER_GUIDE.md) for:
- Non-technical explanation
- Step-by-step setup instructions
- How to use the application
- Troubleshooting tips

### For Developers

See [README.md](./README.md) for:
- Technical architecture
- API documentation
- Development workflow
- Testing instructions

## Quick Start

```bash
# 1. Make sure Docker Desktop is running
# 2. Navigate to the project
cd capital-gains

# 3. Start everything
docker compose up --build

# 4. Open your browser
# Go to: http://localhost:3000
```

That's it! The application will be running.

## Key Features

- ✅ **No Authentication Required** - Demo mode for easy testing
- ✅ **Real-time Price Updates** - Prices change as people trade
- ✅ **Order Matching** - Automatic matching of buy/sell orders
- ✅ **Position Tracking** - Know exactly what you own
- ✅ **Profit/Loss Calculation** - Automatic P/L tracking
- ✅ **Market Resolution** - Final payouts when events happen

## Project Structure

```
capital-gains/
├── backend/          # FastAPI Python backend
│   ├── app/         # Application code
│   ├── alembic/     # Database migrations
│   └── tests/       # Backend tests
├── frontend/         # Next.js React frontend
│   └── src/         # Source code
├── compose.yml       # Docker Compose configuration
├── README.md         # Technical documentation
├── USER_GUIDE.md     # User-friendly guide
└── OVERVIEW.md       # This file
```

## Learn More

- **What is a prediction market?** - [Wikipedia](https://en.wikipedia.org/wiki/Prediction_market)
- **How do order books work?** - [Investopedia](https://www.investopedia.com/terms/o/order-book.asp)

---

**Ready to start?** Check out [USER_GUIDE.md](./USER_GUIDE.md) for detailed setup instructions!

