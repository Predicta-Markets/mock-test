# Capital Gains Prediction Market - User Guide

## 📖 What is a Prediction Market?

A **prediction market** is like a stock market, but instead of buying shares in companies, you're buying shares in the outcome of future events. Think of it as a way to bet on whether something will happen or not, but in a more structured, market-driven way.

### Simple Example

Imagine you want to bet on whether it will rain tomorrow. In a prediction market:

- You can buy a "YES" share (betting it WILL rain) for, say, 60 cents
- Or buy a "NO" share (betting it WON'T rain) for 40 cents
- Notice: YES (60) + NO (40) = 100 cents total

If it rains tomorrow:
- Your YES shares are worth 100 cents each (you win!)
- NO shares are worth 0 cents (you lose)

If it doesn't rain:
- Your NO shares are worth 100 cents each (you win!)
- YES shares are worth 0 cents (you lose)

The prices change based on what people think will happen. If more people think it will rain, YES shares get more expensive and NO shares get cheaper.

---

## 🎯 What is This Project?

**Capital Gains** is a working prediction market platform where you can:

1. **Create markets** - Ask any yes/no question (e.g., "Will Bitcoin reach $100,000 by 2025?")
2. **Trade shares** - Buy or sell YES/NO shares at prices you choose
3. **Track your positions** - See how many shares you own and your profit/loss
4. **Resolve markets** - When the event happens, determine the winner and pay out

### Key Features

- **Binary Markets**: Every market has only two outcomes - YES or NO
- **Automatic Pricing**: Prices always add up to 100 (if YES costs 70, NO costs 30)
- **Order Matching**: When you want to buy, the system finds someone who wants to sell (and vice versa)
- **Position Tracking**: The system remembers what you bought and at what price
- **Profit/Loss Calculation**: Automatically calculates your gains or losses

---

## 🔄 How It Works (Step by Step)

### 1. Creating a Market

You start by creating a market with a question:
- **Question**: "Will the temperature exceed 80°F tomorrow?"
- **Initial YES Price**: Let's say 50 cents (so NO is automatically 50 cents)
- **Description**: Optional details about the market

The system creates the market and sets up the initial prices.

### 2. Trading Shares

Once a market exists, you can trade:

**Buying YES shares:**
- You say: "I want to buy 10 YES shares at 55 cents each"
- The system tries to match you with someone selling NO shares
- If matched, you get the shares and the market price updates
- If not fully matched, you might get some shares immediately and the rest wait in the order book

**Selling shares:**
- You can only sell shares you already own
- You say: "I want to sell 5 YES shares at 60 cents each"
- The system tries to match you with buyers
- If not matched, your order waits in the order book for someone to buy later

### 3. Price Discovery

Prices change automatically based on trades:
- If many people buy YES shares, the YES price goes up and NO price goes down
- The system ensures YES + NO always equals 100 cents

### 4. Tracking Your Position

The system tracks:
- **Quantity**: How many YES and NO shares you own
- **Average Cost**: What you paid on average (if you bought at different prices)
- **Realized P/L**: Profit or loss from shares you've already sold

### 5. Resolving a Market

When the event happens (or you decide to end the market):
- Someone clicks "Resolve YES" or "Resolve NO"
- The system calculates final payouts:
  - **Winning side**: Gets 100 cents per share
  - **Losing side**: Gets 0 cents per share
- All positions are cleared and the market is closed

---

## 💡 Real-World Example

Let's walk through a complete example:

### Step 1: Create Market
**Question**: "Will it snow on Christmas Day?"
**Initial YES price**: 30 cents (NO = 70 cents)

### Step 2: You Buy Shares
You buy 20 YES shares at 30 cents each = $6.00 total
- You now own 20 YES shares
- Your average cost: 30 cents per share

### Step 3: Price Moves
More people buy YES shares, price moves to 50 cents
- YES = 50 cents, NO = 50 cents

### Step 4: You Sell Some
You sell 10 YES shares at 50 cents each = $5.00
- You still own 10 YES shares
- Your profit: (50 - 30) × 10 = $2.00 profit
- Your average cost is still 30 cents for the remaining 10 shares

### Step 5: Market Resolves
Christmas Day arrives - it snows!
- Market resolves to YES
- Your 10 remaining YES shares pay out: 10 × 100 cents = $10.00
- Your total profit: $2.00 (from selling) + $7.00 (from resolution) = $9.00

---

## 🛠️ Setup Instructions

### Prerequisites

Before you begin, make sure you have installed:

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
   - This runs all the services (database, backend, frontend) in containers
   - Available for Windows, Mac, and Linux

2. **Git** (optional) - If you want to clone the repository
   - Usually pre-installed on Mac/Linux
   - [Download for Windows](https://git-scm.com/download/win)

### Step-by-Step Setup

#### Step 1: Navigate to the Project

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and go to the project folder:

```bash
cd capital-gains
```

#### Step 2: Start Everything with Docker

Docker Compose will automatically:
- Start the database (PostgreSQL)
- Start the backend API server
- Start the frontend web application
- Set up all connections between them

Run this command:

```bash
docker compose up --build
```

**What this does:**
- `--build` builds the Docker images for the first time
- Downloads PostgreSQL if needed
- Installs all dependencies
- Starts all three services

**First time setup takes 2-5 minutes** - be patient while it downloads and builds everything.

You'll see lots of output in your terminal. When you see messages like:
- `Uvicorn running on http://0.0.0.0:8000`
- `Ready in X seconds`

Everything is ready!

#### Step 3: Access the Application

Once everything is running:

1. **Open your web browser**
2. **Go to**: `http://localhost:3000`
3. You should see the prediction market homepage!

**API Documentation**: `http://localhost:8005/docs` (optional - for developers)

#### Step 4: Stop the Application

When you're done:

1. Go back to your terminal
2. Press `Ctrl + C` (or `Cmd + C` on Mac)
3. Wait for services to stop
4. Or run: `docker compose down` to stop and remove containers

---

## 🎮 Using the Application

### Homepage (`http://localhost:3000`)

- **View all markets**: See a list of all prediction markets
- **Create new market**: Click "New Market" button
- **View market details**: Click "Open market" on any market card

### Market Detail Page

When you open a market, you'll see:

1. **Market Information**
   - The question
   - Current YES and NO prices
   - Market status (Open or Resolved)

2. **Your Positions**
   - How many YES/NO shares you own
   - Your average cost per share
   - Your realized profit/loss

3. **Order Book**
   - See what orders are waiting to be matched
   - Shows prices and quantities available

4. **Place Order Form**
   - Choose: YES or NO side
   - Choose: BUY or SELL
   - Enter: Price (0-100) and Quantity
   - Click "Submit Order"

5. **Resolve Market**
   - Click "Resolve YES" or "Resolve NO" to end the market
   - This pays out all remaining shares

---

## 🔧 Troubleshooting

### Problem: "Port already in use"

**Solution**: Another application is using port 3000 or 8005. Either:
- Stop the other application
- Or change the ports in `compose.yml`

### Problem: "Cannot connect to database"

**Solution**: Wait a bit longer - the database might still be starting up. Check the terminal output for database messages.

### Problem: "Docker not running"

**Solution**: Make sure Docker Desktop is running. Look for the Docker icon in your system tray/menu bar.

### Problem: Changes not showing up

**Solution**: The services have live reload enabled. If changes don't appear:
- Check the terminal for error messages
- Try refreshing your browser
- Restart with `docker compose restart`

### Problem: Want to start fresh

**Solution**: Reset everything:
```bash
docker compose down -v  # Removes containers and volumes (deletes data)
docker compose up --build  # Start fresh
```

---

## 📊 Understanding the Numbers

### Prices
- Prices are in **cents** (0-100)
- YES price + NO price always equals 100
- Example: YES = 65 cents, NO = 35 cents

### Quantities
- You can buy/sell any whole number of shares
- Example: 1, 10, 100, 1000 shares

### Costs
- **Total Cost** = Price × Quantity
- Example: 20 shares at 50 cents = 1,000 cents ($10.00)

### Profit/Loss
- **Realized P/L**: Profit from shares you've already sold
- **Unrealized P/L**: Potential profit from shares you still own (calculated at resolution)
- Green numbers = profit, Red numbers = loss

---

## 🎓 Key Concepts Explained

### Order Book
Think of it like a bulletin board where people post "I want to sell X shares at Y price" and others can match with them.

### Order Matching
When you want to buy, the system automatically finds the best available seller and matches you together.

### Weighted Average Cost
If you buy shares at different prices:
- First: 10 shares at 40 cents
- Then: 10 shares at 60 cents
- Your average cost: 50 cents per share (not 40 or 60)

### Market Resolution
When the event actually happens, the market closes and everyone gets paid based on whether they picked the winning side.

---

## 🚀 Next Steps

1. **Create your first market** - Think of a yes/no question
2. **Place some orders** - Try buying and selling shares
3. **Watch prices move** - See how trading affects prices
4. **Resolve a market** - See how payouts work

Have fun exploring prediction markets!

---

## 📝 Notes

- **No Authentication**: This is a demo - anyone can create markets and trade
- **No Real Money**: This is a demonstration platform
- **Data Persistence**: Your markets and trades are saved in the database
- **Live Reload**: Changes to code automatically reload (for developers)

---

## 🆘 Need Help?

If you encounter issues:
1. Check the terminal output for error messages
2. Make sure Docker Desktop is running
3. Try restarting: `docker compose restart`
4. Check that ports 3000 and 8005 aren't in use by other applications

